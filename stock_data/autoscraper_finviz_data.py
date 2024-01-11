from autoscraper import AutoScraper
import pandas as pd

# Fetches financial data for a list of tickers from Finviz using AutoScraper.
def fetch_finviz_data(tickers, scraper_rule_path):
    # Create an instance of AutoScraper
    scraper = AutoScraper()

    # Load scraper rules from the specified file path
    scraper.load(scraper_rule_path)

    # Iterate over the tickers and scrape data
    for ticker in tickers:
        url = f'https://finviz.com/quote.ashx?t={ticker}'
        result = scraper.get_result(url)[0]

        # Extract attributes and values
        index = result.index('Index')
        attributes, values = result[index:], result[:index]

        # Create a DataFrame and display data
        df = pd.DataFrame(zip(attributes, values), columns=['Attributes', 'Values'])
        print(f'\n{ticker} Data:')
        print(df.set_index('Attributes'))

# Example usage
tickers = ['SCHB', 'AMZN', 'AAPL', 'MSFT', 'TSLA', 'AMD', 'NFLX']
scraper_rule_path = '../finviz_table'
fetch_finviz_data(tickers, scraper_rule_path)