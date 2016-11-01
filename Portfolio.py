from Security import Security
from Holding import Holding
import HelperFunctions
import numpy as np

class Portfolio(object):
	def add_holding(self, holding):
		self.holdings[holding.security.symbol] = holding

	def remove_holding(self, symbol):
		del self.holdings[symbol]

	def get_holding(self, symbol):
		return self.holdings[symbol]

	# Updates the holding by executing a given function with the supplied holding. Used to update values, prices, etc.
	def update_holding(self, symbol, func):
		func(self.holdings[symbol])

	# Moves funds from the sell holding to the buy holding, by the percent_to_transact. Subtracts an optional fee.
	def transact(self, buy, sell, day, percent_to_transact):
		# sell
		cash_to_sell = percent_to_transact * self.holdings[sell].value[day]
		shares_to_sell = cash_to_sell/self.holdings[sell].price(day)
		self.holdings[sell].shares[day] -= shares_to_sell

		# buy
		cash_pool = cash_to_sell - self.fee
		shares = cash_pool / self.holdings[buy].price(day)
		self.holdings[buy].shares[day] += shares

		# update
		self.holdings[sell].value[day] = self.holdings[sell].price(day) * self.holdings[sell].shares[day]
		self.holdings[buy].value[day] = self.holdings[buy].price(day) * self.holdings[buy].shares[day]

	def generate_new_portfolio(self, symbols, align_data = True, max_alignment = -1):
		securities = [Security(s) for s in symbols]
		
		if align_data:
			series = [s.data for s in securities]
			aligned_series = HelperFunctions.align_data(series, max_alignment)
			for c, s in enumerate(securities):
				s.set_data(s.symbol, aligned_series[c])

		self.holdings = dict([[s.symbol,Holding(s)] for s in securities])
		self.max_day = np.min([np.size(self.holdings[s].security.data) for s in self.holdings])
		
	# Gets the percentage share of a holding in the portfolio by value
	def get_holding_percentage(self, symbol):
		h = self.holdings[symbol]
		return h.value[self.day]/self.get_net_value()

	# Gets the total value of the portfolio
	def get_net_value(self, day = None):
		if day is None:
			day = self.day
		return reduce(np.add, [self.holdings[x].value[day] for x in self.holdings])

	# Gets the length of the shortest holding
	def get_max_day(self):
		return self.max_day

	# Updates the transaction fees
	def change_fee(self, fee):
		self.fee = fee

	# Enables or disables the use of rebalancing strategies
	def set_rebalance(self, bool):
		self.rebalance = bool

	# Updates the investment allocation with new capital.
	def invest(self, amount_invested, day):
		self.day = day

		# Update holdings for today before adding any new capital
		for h in self.holdings:
			self.holdings[h].update(day)

		# Add any outstanding cash to pool
		if self.cash > 0:
			amount_invested += self.cash
			self.cash = 0

		total_value = self.get_net_value()
		if total_value > 0:
			investments = dict([(x, self.get_holding_percentage(x) * amount_invested) for x in self.holdings])
			for h in self.holdings:
				self.holdings[h].invest(investments[h], day)
		elif len(self.holdings) > 0:
			investments = dict([(x, amount_invested / len(self.holdings)) for x in self.holdings])
			for h in self.holdings:
				self.holdings[h].invest(investments[h], day)
		else:
			self.cash += amount_invested

	def __init__(self, holdings):
		self.fee = 14
		self.daily_investment = 10
		self.rebalance = True
		self.holdings = holdings
		self.cash = 0
		self.cagr = []
		self.draw_down = []

		if holdings is not None:
			self.max_day = reduce(np.min, [len(self.holdings[s].security) for x in self.holdings])


