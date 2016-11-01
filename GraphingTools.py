import matplotlib.pyplot as plt
from Portfolio import Portfolio
plt.ion()


def plot_portfolio(portfolio):
	fig = plt.figure()
	ax = fig.add_subplot('111')
	years = portfolio.max_day / 252
	days = [(float(x)/252 + 2015-years) for x in range(portfolio.max_day)]
	ax.plot(days, [portfolio.get_net_value(x) for x in range(portfolio.max_day)], label='Total')
	holdings = [portfolio.holdings[x] for x in portfolio.holdings]
	holdings.sort(key=lambda x: x.security.symbol)
	holdings[::-1]

	for series in holdings:
		ax.plot(days, series.value, label=series.security.symbol)

	plt.legend(loc='best')
	fig.canvas.show()
	raw_input()