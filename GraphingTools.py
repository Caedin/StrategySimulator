import matplotlib.pyplot as plt
import datetime
from Portfolio import Portfolio
plt.ion()


def plot_portfolio(portfolio, params = None):
	fig = plt.figure()
	ax = fig.add_subplot('111')
	years = portfolio.max_day / 252

	days = [(float(x)/252 + datetime.datetime.now().year-years) for x in range(portfolio.max_day)]

	# Plot totals
	ax.plot(days, [portfolio.value[x] for x in range(portfolio.max_day)], label='Total')
	for series in portfolio.holdings.values():
		ax.plot(days, series.value, label=series.security.symbol)
	plt.legend(loc='best')
	fig.canvas.show()

	# Plot Security Values
	fig = plt.figure()
	ax = fig.add_subplot('111')
	for series in portfolio.holdings.values():
		ax.plot(days, series.security.data, label=series.security.symbol)
	plt.legend(loc='best')
	fig.canvas.show()


	# Plot MA
	if params is not None and 'moving_average' in params:
		fig = plt.figure()
		ax = fig.add_subplot('111')
		ax.plot(days, params['moving_average_base'].data, label=params['moving_average_base'].symbol)
		ax.plot(days, params['moving_average'].data, label=params['moving_average_base'].symbol + 'MA')

		plt.legend(loc='best')
		fig.canvas.show()
	raw_input('Press any key to continue . . .')

