import Simulator
import HelperFunctions as hf
import Strategies
import GraphingTools
import numpy as np
import json
import HelperFunctions

from ParameterPool import ParameterPool
from Security import Security
from Portfolio import Portfolio
from Holding import Holding

from Queue import Queue

# Caching to reduce recomputation of simulations
cache = {}
work = Queue()
results = Queue()
parallel_mode = False

# Sets the caching mode to local or multiprocessing
def set_multiprocessing_mode():
	global cache, work, results, parallel_mode
	from multiprocessing import Manager, Queue as pqueue
	parallel_mode = True
	# Migrate the cache to the parallel cache
	man = Manager()
	multi_cache = man.dict()
	for x in cache:
		multi_cache[x] = cache[x]
	cache = multi_cache

	# Migrate the queues to the parallel queues
	pwork = pqueue()
	presults = pqueue()

	while work.empty() == False:
		pwork.put(work.get())
	while presults.empty() == False:
		presults.put(results.get())

	work = pwork
	results = presults

# Executes a simulation, pulling from the multiprocessor cache if possible.
def execute_simulation(portfolio, strategy, cache_key = None, overwrite_cache = False):
	if cache_key is None:
		return Simulator.simulate(portfolio, strategy)
	else:
		global cache
		if overwrite_cache == True:
			cache[cache_key] = Simulator.simulate(portfolio, strategy)

		if cache_key in cache:
			return cache[cache_key]
		else:
			cache[cache_key] = Simulator.simulate(portfolio, strategy)
			return cache[cache_key]
	
def generate_chart_moving_average():
	stk1 = raw_input("Enter Stock 1: ")
	stk2 = raw_input("Enter Stock 2: ")
	stock1_leverage_rate = float(raw_input("Stock 1 Leverage: "))
	moving_window = int(raw_input("Enter moving average window in days: "))
	
	securities = [Security(stk1, leverage = stock1_leverage_rate), stk2]
	portfolio = Portfolio(None)
	portfolio.generate_new_portfolio(securities)

	moving_average = Security(stk1)
	moving_average.set_data(stk1, moving_average.generate_moving_average(moving_window))
	
	params = {}
	params['primary'] = securities[0].symbol
	params['secondary'] = stk2
	params['moving_average'] = moving_average

	cache_key = { 'rebalancing_function': Strategies.moving_average_rebalancing.__name__, 'primary':stk1, 'secondary':stk2, 'primary_leverage':stock1_leverage_rate, 'moving_window': moving_window }
	cache_key = json.dumps(cache_key)

	strategy = Strategies.Strategy(Strategies.moving_average_rebalancing, params)

	portfolio = execute_simulation(portfolio, strategy, cache_key)
	GraphingTools.plot_portfolio(portfolio)


def load_simulation_parameters(functions):
	global work

	# Grab parameters
	parameters = {
		'rebalancing_function' : functions['rebalancing_function'](),
		'primary' : functions['primary'](),
		'secondary' : functions['secondary'](),
		'primary_leverage' : functions['primary_leverage'](),
		'moving_window' : functions['moving_window']()
	}

	# Load paramaters
	p = ParameterPool()
	for axis in parameters:
		for value in parameters[axis]:
			p.add_value(value, axis)

	for num, w in enumerate(p.data):
		print num, ' parameters loaded'
		work.put(p.data[w])

def generate_dataset(parameters):
	securities = [Security(parameters['primary'], leverage = parameters['primary_leverage']), parameters['secondary']]
	portfolio = Portfolio(None)
	portfolio.generate_new_portfolio(securities)

	moving_average = Security(parameters['primary'])
	moving_average.set_data(parameters['primary'], moving_average.generate_moving_average(parameters['moving_window']))
	
	params = {}
	params['primary'] = parameters['primary']
	params['secondary'] = parameters['secondary']
	params['moving_average'] = moving_average

	strategy = Strategies.Strategy(parameters['rebalancing_function'], params)
	return portfolio, strategy

def parallel_consume_work(work, result):
	while work.empty() == False:
		p = work.get()

		portfolio, strategy = generate_dataset(p)

		p['rebalancing_function'] = p['rebalancing_function'].__name__
		cache_key = json.dumps(p)
		r = execute_simulation(portfolio, strategy, cache_key)

		result.put((cache_key, r.cagr[-1], min(r.draw_down), r.get_net_value()))

def consume_results(output, results):
	print 'Gathering results ' + str(results.qsize()) + ' ...' 
	result_set = {}
	c = 0
	while results.empty() == False:
		r = results.get()
		c+=1
		result_set[c] = r
	
	with open(output, 'w') as outputfile:
		print 'Savings results ' + str(len(result_set)) + ' ...'
		for r in result_set.values():
			outputfile.write(','.join([str(x) for x in r]) + '\n')

def batch_simulate(output, parallel = False, cache = True):
	from multiprocessing import Process

	global work, results

	if parallel:
		set_multiprocessing_mode()
		processes = []
		for x in xrange(8):
			p = Process(target = parallel_consume_work, args=(work, results))
			processes.append(p)
		for p in processes:
			print 'Consumption Process Started'
			p.start()
		for p in processes:
			p.join()


	else:
		count = 0
		while work.empty() == False:
			count += 1
			p = work.get()
			portfolio, strategy = generate_dataset(p)

			p['rebalancing_function'] = p['rebalancing_function'].__name__
			cache_key = json.dumps(p)
			result = execute_simulation(portfolio, strategy, cache_key)

			results.put((cache_key, result.cagr[-1], min(result.draw_down), result.get_net_value()))

			print count, ' simulations executed'

	consume_results(output, results)


