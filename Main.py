import SimulationOrchestrator
import Strategies

if __name__ == '__main__':
	paramater_generators = {
		'rebalancing_function' : (lambda : [Strategies.moving_average_rebalancing]),
		'primary' : (lambda : ['sp_daily', 'nasdaq']),
		'secondary' : (lambda : ['cash']),
		'primary_leverage' : (lambda : [1]),
		'moving_window' : (lambda : xrange(5, 500, 50))
	}

	SimulationOrchestrator.load_simulation_parameters(paramater_generators)
	SimulationOrchestrator.batch_simulate('test.csv', parallel = False)

	
	
