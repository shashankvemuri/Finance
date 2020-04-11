import pandas as pd
import numpy as np


def main():
	df_symbols = pd.read_csv("sp500-constituents.csv")
	df_data = pd.read_csv("data.csv")

	#Correct column name
	df_data.rename(index=str, columns={df_data.columns[0]: "Symbol"}, inplace=True)

	sLength = len(df_data['Symbol'])
	#df_data = df_data.assign(Industry=pd.Series(np.random.randn(sLength)).values)
	print(df_data.head())
	print(df_symbols.head())
	
	# Merge symbols with data df to get name of company and industry
	df_data = df_data.join(df_symbols.set_index('Symbol'), on="Symbol")
	df_data.dropna(thresh=10, inplace=True)
	df_data.to_csv("data2.csv")

if __name__ == "__main__":
	main()