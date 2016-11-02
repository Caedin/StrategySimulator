import HelperFunctions

# runs a simulation using the provided portfolio and rebalancing method
def simulate(portfolio, strategy):
	day = 0
	daily_investment = 10
	trade_count = 0
	refactor_days = 3
	last_trade_day = 0

	for day in xrange(0, portfolio.get_max_day()):
		# Update cash balances / invest
		portfolio.invest(daily_investment, day)

		# Rebalance if able, and needed
		# Must be outside of the delay window, must have rebalancing enabled, and must have enough funds to cover fees
		if (day-last_trade_day) >= refactor_days and portfolio.rebalance and portfolio.get_net_value() > portfolio.fee:
			isTradeExecuted = strategy.execute_strategy(portfolio, day)
			if isTradeExecuted:
				trade_count += 1
				last_trade_day = day

	# Calculate some interesting data from the simulation, and return the experiment
	portfolio.cagr = [HelperFunctions.calc_cagr(daily_investment * x, portfolio.get_net_value(x), float(x)/252) for x in range(portfolio.get_max_day())]
	portfolio.draw_down = HelperFunctions.generate_draw_down([portfolio.get_net_value(x) for x in range(portfolio.get_max_day())])
	return portfolio