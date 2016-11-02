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
	from multiprocessing import Manager
	parallel_mode = True
	# Migrate the cache to the parallel cache
	man = Manager()
	multi_cache = man.dict()
	for x in cache:
		multi_cache[x] = cache[x]
	cache = multi_cache

	# Migrate the queues to the parallel queues
	pwork = man.Queue()
	presults = man.Queue()

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
	portfolio.investment_ratios = {parameters['primary'] : 1, parameters['secondary'] : 0}

	moving_average = Security(parameters['primary'])
	moving_average.set_data(parameters['primary'], moving_average.generate_moving_average(parameters['moving_window']))
	
	params = {}
	params['primary'] = parameters['primary']
	params['secondary'] = parameters['secondary']
	params['moving_average'] = moving_average

	strategy = Strategies.Strategy(parameters['rebalancing_function'], params)
	return portfolio, strategy

# Function for consuming work from the work queue.
def parallel_consume_work(work, result, pid):
	while work.empty() == False:
		# Get work
		p = work.get()
		if work.qsize() % 100 == 0:
			print 'Estimated work items remaining: ' + str(work.qsize())

		# Execute Simulation
		portfolio, strategy = generate_dataset(p)
		p['rebalancing_function'] = p['rebalancing_function'].__name__
		cache_key = json.dumps(p)
		r = execute_simulation(portfolio, strategy, cache_key)

		# Save results
		result.put((cache_key, r.cagr[-1], min(r.draw_down), r.trade_count, r.value[-1]))
		work.task_done()

def consume_results(output, results):
	print 'Gathering results ' + str(results.qsize()) + ' ...' 
	result_set = {}
	c = 0
	while results.empty() == False:
		r = results.get()
		result_set[c] = r
		c+=1
	
	with open(output, 'w') as outputfile:
		print 'Savings results ' + str(len(result_set)) + ' ...'
		results = result_set.values()
		results.sort(key = lambda x: x[-1])
		results = results[::-1]

		for r in results:
			param_key = json.loads(r[0])
			params = []
			for field in param_key:
				params.append(str(field) + ':' + str(param_key[field]))

			params.sort(key = lambda x: x)
			outputfile.write(','.join(params) + ',' + ','.join([str(x) for x in r[1:]]) + '\n')

def batch_simulate(output, parallel = False, cache = True):
	import multiprocessing
	from multiprocessing import Process
	global work, results

	if parallel:
		set_multiprocessing_mode()
		for x in xrange(multiprocessing.cpu_count()):
			p = Process(target = parallel_consume_work, args=(work, results, x))
			p.start()
		work.join()

	else:
		count = 0
		while work.empty() == False:
			count += 1
			p = work.get()
			portfolio, strategy = generate_dataset(p)

			p['rebalancing_function'] = p['rebalancing_function'].__name__
			cache_key = json.dumps(p)
			r = execute_simulation(portfolio, strategy, cache_key)

			results.put((cache_key, r.cagr[-1], min(r.draw_down), r.trade_count, r.value[-1]))

			print count, ' simulations executed'

	consume_results(output, results)


