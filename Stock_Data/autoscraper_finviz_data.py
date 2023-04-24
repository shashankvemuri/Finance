# Importing required modules
from autoscraper import AutoScraper
import pandas as pd

# Setting display options to show all rows of dataframe
pd.set_option('display.max_rows', None)

# List of tickers to fetch data for
tickers = ['SCHB', 'AMZN', 'AAPL', 'MSFT', 'TSLA', 'AMD', 'NFLX']

# Creating an instance of AutoScraper and loading previously created scraper rules
scraper = AutoScraper()
scraper.load('../finviz_table')

# Fetching data for each ticker
for ticker in tickers:
    url = f'https://finviz.com/quote.ashx?t={ticker}'

    # Using AutoScraper to extract data from the URL
    result = scraper.get_result(url)[0]

    # Separating the extracted data into attributes and their corresponding values
    index = result.index('Index')
    df = pd.DataFrame(zip(result[index:], result[:index]), columns = ['Attributes', 'Values'])

    # Displaying the extracted data for each ticker
    print (f'\n{ticker} Data: ')
    print (df.set_index('Attributes'))