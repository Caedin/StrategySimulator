# Returns new a new series of data, with indexes aligning
def align_data(series, min_backtest_time=-1):
	if min_backtest_time==-1:
		min_backtest_time = min([len(x) for x in series])
		
	series = [x[len(x) - min_backtest_time : ] for x in series]
	return series
	
# Calculates the Compound Annual Growth Rate of an investment
def calc_cagr(investment, returns, years):
	try:
		cagr = (float(returns) / float(investment))
		cagr = cagr ** ( 1.0 / float(years) )
		cagr = cagr - 1.0
		return cagr
	except:
		return 0.0

# Generates a series of max draw downs experienced
def generate_draw_down(data):
	max = panda.rolling_max(data, len(data), min_periods = 1)
	draw_down = (data - max) / max
	return draw_down
