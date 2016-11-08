import numpy as np
class RandomSampler(object):
	def __init__(self, security):
		rates_of_change = ((security.data[1:] - security.data[:-1]) / security.data[:-1]) + 1
		mu = np.average(rates_of_change)
		sigma = np.std(rates_of_change)
		self.sample = 100 * np.cumprod(np.random.normal(mu, sigma, len(security.data))


