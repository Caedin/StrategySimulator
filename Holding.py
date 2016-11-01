import numpy as np

class Holding(object):
	def price(self, day):
		return self.security.data[day]

	def invest(self, amount, day):
		self.update(day)
		p = self.price(day)

		self.shares[day] = self.shares[day] + float(amount)/p
		self.value[day] = p * self.shares[day]

	def update(self, day):
		if day > 0:
			prev_val = self.value[day-1]
			prev_shares = self.shares[day-1]
		else:
			prev_val = 0
			prev_shares = 0

		self.value[day] = prev_val
		self.shares[day] = prev_shares

	def __init__(self, security):
		self.security = security
		self.shares = np.zeros(len(security.data))
		self.value = np.zeros(len(security.data))

