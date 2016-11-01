import Simulator
import HelperFunctions as hf
import Strategies
import GraphingTools
import numpy as np

from Security import Security
from Portfolio import Portfolio
from Holding import Holding
	
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

	strategy = Strategies.Strategy(Strategies.moving_average_rebalancing, params)
	portfolio = Simulator.simulate(portfolio, strategy)
	GraphingTools.plot_portfolio(portfolio)

