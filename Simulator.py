import HelperFunctions
import numpy as np

# runs a simulation using the provided portfolio and rebalancing method
def simulate(portfolio, strategy):
	day = 0
	daily_investment = 0
	trade_count = 0
	refactor_days = 3
	last_trade_day = 0
	max_day = portfolio.get_max_day()
	starting_cash = portfolio.cash

	for day in xrange(0, max_day):
		# Update cash balances / invest
		portfolio.invest(daily_investment, day)

		# Rebalance if able, and needed
		# Must be outside of the delay window, must have rebalancing enabled, and must have enough funds to cover fees
		if (day-last_trade_day) >= refactor_days and portfolio.rebalance and portfolio.value[day] > portfolio.fee:
			isTradeExecuted = strategy.execute_strategy(portfolio, day)
			if isTradeExecuted:
				trade_count += 1
				last_trade_day = day

	# Calculate some interesting data from the simulation, and return the experiment
	years = np.arange(0, max_day, 1) / 252.0
	portfolio.cagr = HelperFunctions.calc_cagr(np.ones(max_day) * starting_cash, portfolio.value, years)
	portfolio.draw_down = HelperFunctions.generate_draw_down(portfolio.value)
	portfolio.trade_count = trade_count
	return portfolio