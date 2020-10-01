from autoscraper import AutoScraper
import pandas as pd
pd.set_option('display.max_rows', None)

tickers = ['SCHB', 'AMZN', 'AAPL', 'MSFT', 'TSLA', 'AMD', 'NFLX']

scraper = AutoScraper()
scraper.load('../finviz_table')

for ticker in tickers:
    url = f'https://finviz.com/quote.ashx?t={ticker}'
    result = scraper.get_result(url)[0]

    index = result.index('Index')
    df = pd.DataFrame(zip(result[index:], result[:index]), columns = ['Attributes', 'Values'])

    print (f'\n{ticker} Data: ')
    print (df.set_index('Attributes'))
