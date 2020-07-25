import yahoo_fin.stock_info as si
import pandas as pd

quote = si.get_quote_table("aapl")
df = pd.DataFrame([quote])
print (df.T)

# get list of Dow tickers
dow_list = si.tickers_dow()
 
# Get data in the current column for each stock's valuation table
dow_stats = {}
for ticker in dow_list:
    temp = si.get_stats_valuation(ticker)
    temp = temp.iloc[:,:2]
    temp.columns = ["Attribute", "Value"]
 
    dow_stats[ticker] = temp
 
# combine all the stats valuation tables into a single data frame
combined_stats = pd.concat(dow_stats)
combined_stats = combined_stats.reset_index()
 
del combined_stats["level_1"]
# update column names
combined_stats.columns = ["Ticker", "Attribute", "Value"]
print(combined_stats)

dow_extra_stats = {}
for ticker in dow_list:
    dow_extra_stats[ticker] = si.get_stats(ticker)
    
combined_extra_stats = pd.concat(dow_extra_stats)
combined_extra_stats = combined_extra_stats.reset_index()
del combined_extra_stats["level_1"]
combined_extra_stats.columns = ["Ticker", "Attribute", "Value"]
print(combined_extra_stats)