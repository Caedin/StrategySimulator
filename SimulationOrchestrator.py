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
	parameters = {}
	parameters['primary'] = raw_input("Enter Stock 1: ")
	parameters['secondary'] = raw_input("Enter Stock 2: ")
	parameters['primary_leverage']  = float(raw_input("Stock 1 Leverage: "))
	parameters['moving_window'] = int(raw_input("Enter moving average window in days: "))
	if parameters['primary_leverage'] != 1:
		parameters['leveraged_moving_average'] = raw_input('Leveraged Moving Average? [True, False]: ')
	else:
		parameters['leveraged_moving_average'] = False

	securities = [Security(parameters['primary'], leverage = parameters['primary_leverage']), parameters['secondary']]
	portfolio = Portfolio(None)
	portfolio.generate_new_portfolio(securities)
	portfolio.set_investments(10, {parameters['primary'] : 1, parameters['secondary'] : 0})

	if parameters['leveraged_moving_average'] == 'True':
		moving_average = Security(parameters['primary'], leverage = parameters['primary_leverage'])
		moving_average_base = Security(parameters['primary'], leverage = parameters['primary_leverage'])
	else:
		moving_average = Security(parameters['primary'])
		moving_average_base = Security(parameters['primary'])

	moving_average.set_data(parameters['primary'], moving_average.generate_moving_average(parameters['moving_window']))

	params = {}
	params['primary'] = parameters['primary']
	params['secondary'] = parameters['secondary']
	params['moving_average'] = moving_average
	params['moving_average_base'] = moving_average_base

	strategy = Strategies.Strategy(Strategies.moving_average_rebalancing, params)
	portfolio = execute_simulation(portfolio, strategy)
	GraphingTools.plot_portfolio(portfolio, params)

	
def generate_chart_windowed_rebalancing():
	parameters = {}
	parameters['primary'] = raw_input("Enter Stock 1: ")
	parameters['secondary'] = raw_input("Enter Stock 2: ")
	parameters['primary_leverage']  = float(raw_input("Stock 1 Leverage: "))
	parameters['primary_ratio'] = float(raw_input("Enter Stock 1 target ratio: "))
	parameters['rebalance_window'] = float(raw_input("Enter rebalancing window: "))

	securities = [Security(parameters['primary'], leverage = parameters['primary_leverage']), parameters['secondary']]
	portfolio = Portfolio(None)
	portfolio.generate_new_portfolio(securities)
	portfolio.set_investments(10, {parameters['primary'] : parameters['primary_ratio'], parameters['secondary'] : 1 - parameters['primary_ratio']})

	params = {}
	params['primary'] = parameters['primary']
	params['secondary'] = parameters['secondary']
	params['rebalance_window'] = parameters['rebalance_window']

	strategy = Strategies.Strategy(Strategies.windowed_rebalancing, params)
	portfolio = execute_simulation(portfolio, strategy)
	GraphingTools.plot_portfolio(portfolio, params)



def load_simulation_parameters(functions):
	global work

	parameters = {}

	# Grab parameters
	for func in functions['rebalancing_function']():
		if func.__name__ == Strategies.moving_average_rebalancing.__name__:
			p = {
				'rebalancing_function' : functions['rebalancing_function'](),
				'primary' : functions['primary'](),
				'secondary' : functions['secondary'](),
				'primary_leverage' : functions['primary_leverage'](),
				'moving_window' : functions['moving_window'](),
				'leveraged_moving_average': functions['leveraged_moving_average']()
			}
		elif func.__name__ == Strategies.windowed_rebalancing.__name__:
			p = {
				'rebalancing_function' : functions['rebalancing_function'](),
				'primary' : functions['primary'](),
				'secondary' : functions['secondary'](),
				'primary_leverage' : functions['primary_leverage'](),
				'primary_ratio' : functions['primary_ratio'](),
				'rebalance_window': functions['rebalance_window']()
			}
		if p:
			for field in p:
				if field not in parameters: 
					parameters[field] = set()
				for item in p[field]:
					parameters[field].add(item)


	# Load paramaters
	p = ParameterPool()
	for axis in parameters:
		for value in parameters[axis]:
			p.add_value(value, axis)
			print 'building parameter set: ', len(p.data)

	for num, w in enumerate(p.data):
		print num, ' parameters loaded'
		work.put(p.data[w])

def generate_dataset(parameters, func):
	if func.__name__ == Strategies.moving_average_rebalancing.__name__:
		securities = [Security(parameters['primary'], leverage = parameters['primary_leverage']), parameters['secondary']]
		portfolio = Portfolio(None)
		portfolio.generate_new_portfolio(securities)
		portfolio.set_investments(10, {parameters['primary'] : 1, parameters['secondary'] : 0})

		if parameters['leveraged_moving_average'] in [True, 'True']:
			moving_average = Security(parameters['primary'], leverage = parameters['primary_leverage'])
			moving_average_base = Security(parameters['primary'], leverage = parameters['primary_leverage'])
		else:
			moving_average = Security(parameters['primary'])
			moving_average_base = Security(parameters['primary'])

		moving_average.set_data(parameters['primary'], moving_average.generate_moving_average(parameters['moving_window']))

		params = {}
		params['primary'] = parameters['primary']
		params['secondary'] = parameters['secondary']
		params['moving_average'] = moving_average
		params['moving_average_base'] = moving_average_base

		strategy = Strategies.Strategy(parameters['rebalancing_function'], params)
		return portfolio, strategy
	elif func.__name__ == Strategies.windowed_rebalancing.__name__:
		securities = [Security(parameters['primary'], leverage = parameters['primary_leverage']), parameters['secondary']]
		portfolio = Portfolio(None)
		portfolio.generate_new_portfolio(securities)
		portfolio.set_investments(10, {parameters['primary'] : parameters['primary_ratio'], parameters['secondary'] : 1 - parameters['primary_ratio']})

		params = {}
		params['primary'] = parameters['primary']
		params['secondary'] = parameters['secondary']
		params['rebalance_window'] = parameters['rebalance_window']

		strategy = Strategies.Strategy(parameters['rebalancing_function'], params)
		return portfolio, strategy
	else:
		raise Exception('Invalid Trading Strategy')

# Function for consuming work from the work queue.
def consume_work(work, result, cache = False):
	while work.empty() == False:
		# Get work
		if work.qsize() % 100 == 0:
			print 'Estimated work items remaining: ' + str(work.qsize())
		p = work.get()

		# Execute Simulation
		portfolio, strategy = generate_dataset(p, p['rebalancing_function'])
		p['rebalancing_function'] = p['rebalancing_function'].__name__

		if 'leveraged_moving_average' in p:
			if p['leveraged_moving_average'] == True:
				p['rebalancing_function'] += ' (L)'
			del p['leveraged_moving_average']



		cache_key = json.dumps(p)
		r = execute_simulation(portfolio, strategy, cache_key, overwrite_cache = cache)

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
				params.append(str(field) + ':' + str(param_key[field]).zfill(3))

			params.sort(key = lambda x: x)
			outputfile.write(','.join(params) + ',' + ','.join([str(x) for x in r[1:]]) + '\n')

def batch_simulate(output, parallel = False, overwrite_cache = False):
	import multiprocessing
	from multiprocessing import Process
	global work, results

	if parallel:
		global parallel_mode
		if parallel_mode == False: set_multiprocessing_mode()
		for x in xrange(multiprocessing.cpu_count()):
			p = Process(target = consume_work, args=(work, results, overwrite_cache))
			p.start()
		work.join()

	else:
		consume_work(work, results, overwrite_cache)

	consume_results(output, results)


