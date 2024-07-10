import pandas as pd
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen

# Set display options for pandas dataframes
pd.set_option('display.max_colwidth', 25)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Input stock symbol
symbol = input('Enter a ticker: ')

# Set up scraper
url = f"https://finviz.com/quote.ashx?t={symbol.strip().upper()}&p=d"
req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
webpage = urlopen(req).read()
html_content = soup(webpage, "html.parser")

# Function to get fundamental ratios
def get_fundamentals():
    try:
        # Get data from finviz and convert to pandas dataframe
        df = pd.read_html(str(html_content), attrs = {"class": "snapshot-table2 screener_snapshot-table-body"})[0]

        # Resetting the combined columns lists
        combined_column1 = []
        combined_column2 = []

        # Looping through the DataFrame to combine data with adjustment for odd number of columns
        for i in range(0, len(df.columns), 2):
            combined_column1.extend(df.iloc[:, i].tolist())
            # Check if the next column exists before adding it, otherwise add None
            if i + 1 < len(df.columns):
                combined_column2.extend(df.iloc[:, i + 1].tolist())
            else:
                combined_column2.extend([None] * len(df))  # Add None for missing values

        # Creating a new DataFrame with the combined columns
        combined_df = pd.DataFrame({'Attributes': combined_column1, 'Values': combined_column2})
        combined_df = combined_df.set_index('Attributes')
        return combined_df
    except Exception as e:
        return e

# Function to get recent news articles
def get_news():
    try:
        news = pd.read_html(str(html_content), attrs={"class": "fullview-news-outer"})[0]
        news.columns = ['DateTime', 'Headline']
        news.set_index('DateTime', inplace=True)
        return news
    except Exception as e:
        return e

# Function to get recent insider trades
def get_insider():
    try:
        insider = pd.read_html(str(html_content), attrs={"class": "body-table"})[0]
        insider.set_index('Date', inplace=True)
        return insider
    except Exception as e:
        return e

# Function to get analyst price targets
def get_price_targets():
    try:
        targets = pd.read_html(str(html_content), attrs={"class": "js-table-ratings"})[0]
        targets.set_index('Date', inplace=True)
        return targets
    except Exception as e:
        return e

# Print out the resulting dataframes for each category
print('Fundamental Ratios:')
print(get_fundamentals())

print('\nRecent News:')
print(get_news())

print('\nRecent Insider Trades:')
print(get_insider())

print('\nAnalyst Price Targets:')
print(get_price_targets())