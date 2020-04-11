import stock_scraper as ss
import pandas as pd

def createList():
	df_symbols = pd.read_csv("sp500-constituents.csv")
	return df_symbols

def main():
	df_symbols = createList()
	interested = ['Market Cap (intraday)', 'Return on Equity', 'Revenue', 'Quarterly Revenue Growth', 
	'Operating Cash Flow', 'Total Cash', 'Total Debt', 'Current Ratio', '52-Week Change',
	'Avg Vol (3 month)', 'Avg Vol (10 day)', '% Held by Insiders']
	technicals = {}
	df = pd.DataFrame(columns=interested)
	for index, each_stock in df_symbols.iterrows():
		tech = ss.scrape_yahoo(each_stock["Symbol"])
		for ind in interested:	
			try:
				df.at[each_stock["Symbol"], ind] = tech[ind]
			except Exception as e:
				print('Failed, exception: ', str(e))
		print(str(index+1) + ": DONE- " + each_stock["Symbol"])
        
	#Correct column name
	df = df.reset_index()
	df.rename(index=str, columns={df.columns[0]: "Symbol"}, inplace=True)

	# Merge symbols with data df to get name of company and industry
	df = df.join(df_symbols.set_index('Symbol'), on="Symbol")

	# Drop rows with excessive NaN values
	df.dropna(thresh=10, inplace=True)

	# Save as CSV
	df.to_csv("data.csv")


if __name__ == "__main__":
	main()