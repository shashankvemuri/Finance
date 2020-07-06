from pytickersymbols import PyTickerSymbols

stock_data = PyTickerSymbols()
countries = stock_data.get_all_countries()
indices = stock_data.get_all_indices()
industries = stock_data.get_all_industries()
print (indices)

nasdaq100 = stock_data.get_stocks_by_index('S&P 500')

print (list(nasdaq100))