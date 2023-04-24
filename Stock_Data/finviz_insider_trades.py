import pandas as pd
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen

pd.set_option('display.max_colwidth', 60)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Define a function to scrape insider trades data from finviz.com
def get_insider_trades():
    try:
        # Set up the scraper
        url = "https://finviz.com/insidertrading.ashx"
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        html = soup(webpage, "html.parser")

        # Extract the insider trades table
        trades = pd.read_html(str(html), attrs={'class': 'body-table'})[0]

        # Rename columns for readability
        trades.columns = ['Ticker', 'Owner', 'Relationship', 'Date', 'Transaction',
                          'Cost', '#Shares', 'Value', '#Shares Total', 'SEC Form 4']

        # Sort trades by date in descending order
        trades = trades.sort_values('Date', ascending=False)

        # Set the date column as index
        trades = trades.set_index('Date')

        # Remove the original date column from dataframe
        trades = trades.drop('Date', axis=1)

        # Remove the first two rows as they are not needed
        trades = trades.iloc[2:]

        # Return the first five rows of insider trades
        return trades.head()

    except Exception as e:
        # Return the error message if any
        return e

# Call the function and print the result
print('\nInsider Trades:')
print(get_insider_trades())