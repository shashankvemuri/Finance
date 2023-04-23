# Import dependencies
import pandas as pd
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

def growth_screener():
    """
    Scrape growth stocks data from FinViz website.

    Returns:
    pandas.DataFrame: DataFrame of growth stocks data with columns Ticker, Company, Sector, Industry, Country, Market Cap, P/E, Price, Change, Volume.
    """
    try:
        frames = []
        # Loop through different pages of FinViz growth screener, each page shows 20 stocks.
        for i in range(1, 105, 20):
            url = (f"https://finviz.com/screener.ashx?v=151&f=fa_epsqoq_o15,fa_epsyoy_pos,fa_epsyoy1_o25,fa_grossmargin_pos,fa_salesqoq_o25,ind_stocksonly,sh_avgvol_o300,sh_insttrans_pos,sh_price_o10,ta_perf_52w50o,ta_sma200_pa,ta_sma50_pa&ft=4&o=-marketcap&r=0{i}")
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req).read()
            html = soup(webpage, "html.parser")

            # Get the second last table from the HTML page which contains the stock data.
            stocks = pd.read_html(str(html))[-2]
            stocks.columns = stocks.iloc[0]
            stocks = stocks[1:]
            stocks = stocks.set_index('Ticker')
            frames.append(stocks)

        # Combine all the DataFrame objects obtained from different pages.
        df = pd.concat(frames)
        df = df.drop_duplicates()
        df = df.drop(columns = ['No.'])
        return df
    except Exception as e:
        return e

df = growth_screener()
tickers = df.index

print ('\nGrowth Stocks Screener: ')
print (df)
print ('\nList of Tickers: ')
# Changed the separator to newline character for better readability.
print (*tickers, sep ='\n')