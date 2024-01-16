# Import dependencies
import pandas as pd
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen

# Set display options for pandas DataFrame
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

def growth_screener():
    try:
        frames = []
        # Loop through different pages of FinViz growth screener
        for i in range(1, 105, 20):
            url = (f"https://finviz.com/screener.ashx?v=151&f=fa_epsqoq_o15,fa_epsyoy_pos,fa_epsyoy1_o25,fa_grossmargin_pos,fa_salesqoq_o25,ind_stocksonly,sh_avgvol_o300,sh_insttrans_pos,sh_price_o10,ta_perf_52w50o,ta_sma200_pa,ta_sma50_pa&ft=4&o=-marketcap&r=0{i}")
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req).read()
            html = soup(webpage, "html.parser")

            # Extracting stock data from the HTML
            stocks = pd.read_html(str(html))[-2]
            stocks = stocks.set_index('Ticker')
            frames.append(stocks)

        # Concatenate all DataFrame objects from different pages
        df = pd.concat(frames)
        df = df.drop_duplicates()
        df = df.drop(columns=['No.'])
        return df
    except Exception as e:
        print(f"Error occurred: {e}")
        return pd.DataFrame()

# Execute the screener and store the result
df = growth_screener()

# Display the results
print('\nGrowth Stocks Screener:')
print(df)

# Extract and print list of tickers
tickers = df.index
print('\nList of Tickers:')
print(*tickers, sep='\n')