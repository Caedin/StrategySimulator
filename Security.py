import numpy as np
import pandas as panda
import urllib

# global cache for loading security objects
raw_data_dictionary = {}

class Security(object):
	global raw_data_dictionary

	# Helpful string functions
	def make_url(self, ticker_symbol):
		return self.base_url + ticker_symbol

	def make_filename(self, ticker_symbol, directory="Stocks"):
		return self.output_path + "/" + directory + "/" + ticker_symbol + ".csv"

	# Fetches data from internet if needed
	def pull_historical_data(self, ticker_symbol, directory="Stocks"):
		import os

		try:
			file_name = self.make_filename(ticker_symbol, directory)
			if os.path.isfile(file_name) == True:
				return file_name
			else:
				urllib.urlretrieve(self.make_url(ticker_symbol), file_name)
				return file_name
		except urllib.ContentTooShortError as e:
			outfile = open(self.make_filename(ticker_symbol, directory), "w")
			outfile.write(e.content)
			outfile.close()

	# Gets data from files/cache
	def get_data(self, stock_file):
		stock_data = []
		if stock_file in raw_data_dictionary:
			from copy import deepcopy
			return deepcopy(raw_data_dictionary[stock_file])
		else:
			with open(stock_file, 'rb') as input:
				input.next()
				stock_data = np.asarray([float(x.split(',')[-1]) for x in input])
			
				if 'gold' in stock_file:
					t = [0.0] * (len(stock_data)*21)
					for count,x in enumerate(stock_data):
						for y in xrange(21):
							t[count*21+y] = x
					stock_data = t
					stock_data = stock_data[::-1]
		
			stock_data = stock_data[::-1]
			raw_data_dictionary[stock_file] = stock_data
			return stock_data

	# Returns a leveraged version of this security
	def generate_leveraged_data(self, leverage_rate):
		data = np.asarray(self.data)
		leveraged_security_data = data[0] * np.insert(np.cumprod((leverage_rate * ((data[1:] - data[:-1])/data[:-1])) + 1), 0, 1)
		return leveraged_security_data

	# Returns a max draw down series for this security
	def generate_draw_down(self, amt_invested):
		max = panda.rolling_max(self.data, len(data), min_periods = 1)
		draw_down = (data - max) / max
		return draw_down

	# Generates a moving average for the security
	def generate_moving_average(self, window_size):
		if window_size > 1:
			return panda.rolling_mean(np.asarray(self.data), window_size, min_periods = 1)
		else:
			return np.asarray(self.data)

	# Sets the data series and symbol for this security
	def set_data(self, symbol, data):
		self.data = data
		self.symbol = symbol

	def __init__(self, symbol, leverage = 1, directory = "Stocks"):
		self.output_path = '.'
		self.base_url = "http://ichart.finance.yahoo.com/table.csv?s="
		self.data = []
		self.symbol = ''

		if type(symbol) is Security:
			self.data = symbol.data
			self.symbol = symbol.symbol
		elif len(symbol) > 0:
			self.data = self.get_data(self.pull_historical_data(symbol, directory))
			self.symbol = symbol

			if leverage > 1:
				self.data = self.generate_leveraged_data(leverage)
