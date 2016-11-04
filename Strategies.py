class Strategy(object):
	# Executes the strategy on a portfolio
	def execute_strategy(self, portfolio, day):
		return self.function(portfolio, day, self.strategy_parameters)

	# Sets up the strategy with a given function
	def __init__(self, func, params, cache_key = None):
		self.function = func
		self.strategy_parameters = params
		self.cache_key = cache_key


# A strategy used for trading based on a deviation of the holding percent from the predefined ratio
def windowed_rebalancing(portfolio, day, parameters):
	primary_stock = parameters['primary']
	secondary_stock = parameters['secondary']
	primary_stock_ratio = portfolio.investment_ratios[primary_stock]
	rebalance_window = parameters['rebalance_window']

	first_stock_portfolio_percent = portfolio.get_holding_percentage(primary_stock, day)

	# Rebalance first_stock -> second_stock
	if first_stock_portfolio_percent > (primary_stock_ratio+rebalance_window):
		amount_wanted = portfolio.get_net_value(day) * (primary_stock_ratio)
		amount_to_sell = portfolio.get_holding(primary_stock).value[day] - amount_wanted
		percent_to_sell = amount_to_sell / portfolio.get_holding(primary_stock).value[day]

		portfolio.transact(secondary_stock, primary_stock, day, percent_to_sell)
		return True

	# Rebalance second_stock -> first_stock
	elif first_stock_portfolio_percent < (primary_stock_ratio-rebalance_window):
		amount_wanted = portfolio.get_net_value(day) * (1-primary_stock_ratio)
		amount_to_sell = portfolio.get_holding(secondary_stock).value[day] - amount_wanted
		percent_to_sell = amount_to_sell / portfolio.get_holding(secondary_stock).value[day]
		
		portfolio.transact(primary_stock, secondary_stock, day, percent_to_sell)
		return True
	return False

# A strategy used for trading based on the simple moving average
def moving_average_rebalancing(portfolio, day, parameters):
	primary = parameters['primary']
	secondary = parameters['secondary']

	price = parameters['moving_average_base'].data[day]
	ma = parameters['moving_average'].data[day]

	primary_pct = portfolio.get_holding_percentage(primary, day) 
	secondary_pct = portfolio.get_holding_percentage(secondary, day) 

	# Rebalance secondary -> primary
	if price > ma and secondary_pct > 0.01:
		portfolio.transact(primary, secondary, day, 1)
		return True

	# Rebalance primary -> secondary
	elif price < ma and primary_pct > 0.01:
		secondary = parameters['secondary']
		portfolio.transact(secondary, primary, day, 1)
		return True
	return False