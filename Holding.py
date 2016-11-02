import numpy as np

class Holding(object):
	def price(self, day):
		return self.security.data[day]

	def invest(self, amount, day):
		p = self.price(day)
		self.shares[day] = self.shares[day-1] + float(amount)/p
		self.value[day] = p * self.shares[day]

	def __init__(self, security):
		self.security = security
		self.shares = np.zeros(len(security.data))
		self.value = np.zeros(len(security.data))

