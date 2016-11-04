import SimulationOrchestrator
import Strategies
import numpy as np
from timeit import default_timer as timer

def run_moving_average_simulations(output_file = 'simulations.csv', parallel = True):
	paramater_generators = {
		'rebalancing_function' : (lambda : [Strategies.moving_average_rebalancing]),
		'primary' : (lambda : ['sp_daily', 'nasdaq']),
		'secondary' : (lambda : ['cash']),
		'primary_leverage' : (lambda : [1,2,3]),
		'moving_window' : (lambda : xrange(0, 500, 1)),
		'leveraged_moving_average': (lambda : [True, False])
	}
	
	t = timer()
	SimulationOrchestrator.load_simulation_parameters(paramater_generators)
	SimulationOrchestrator.batch_simulate(output_file, parallel = parallel)
	print timer() - t

def run_windowed_rebalancing_simulations(output_file = 'windowed_rebalancing.csv',  parallel = True):
	paramater_generators = {
		'rebalancing_function' : (lambda : [Strategies.windowed_rebalancing]),
		'primary' : (lambda : ['nasdaq']),
		'secondary' : (lambda : ['cash']),
		'primary_leverage' : (lambda : [1,2,3]),
		'primary_ratio' : (lambda : np.arange(0.4, 1, 0.01)),
		'rebalance_window': (lambda :np.arange(0.35, 0.5, 0.01))
	}

	t = timer()
	SimulationOrchestrator.load_simulation_parameters(paramater_generators)
	SimulationOrchestrator.batch_simulate(output_file, parallel = parallel)
	print timer() - t

if __name__ == '__main__':
	run_moving_average_simulations()
	run_windowed_rebalancing_simulations()