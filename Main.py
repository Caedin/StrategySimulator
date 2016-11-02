import SimulationOrchestrator
import Strategies
from timeit import default_timer as timer

if __name__ == '__main__':
	paramater_generators = {
		'rebalancing_function' : (lambda : [Strategies.moving_average_rebalancing]),
		'primary' : (lambda : ['sp_daily', 'nasdaq']),
		'secondary' : (lambda : ['cash']),
		'primary_leverage' : (lambda : [1,2,3]),
		'moving_window' : (lambda : xrange(5, 500, 1))
	}

	t = timer()
	SimulationOrchestrator.load_simulation_parameters(paramater_generators)
	SimulationOrchestrator.batch_simulate('simulations.csv', parallel = True)
	print timer() - t

	
	
