import pandas as pd
import json
import finviz

pd.set_option('display.max_colwidth', 25)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Input
symbol = input('Enter a ticker: ')

def get_fundamentals(ticker):
    try:
        fundamentals = json.dumps(finviz.get_stock(ticker))
        fundamentals = pd.read_json(fundamentals, orient='index')
        fundamentals = fundamentals.reset_index()
        fundamentals.columns = ['Attributes', 'Values']
        fundamentals = fundamentals.set_index('Attributes')
        return fundamentals
    except Exception as e:
        return e
    
def get_news(ticker):
    try:
        news = finviz.get_news(ticker)
        news = pd.DataFrame(news, columns=['Headline', 'Link'])
        news = news.set_index('Headline')
        return news
    except Exception as e:
        return e

def get_insider(ticker):
    try:
        insider = finviz.get_insider(ticker)
        insider = pd.DataFrame(insider)
        insider = insider.set_index('Date')
        return insider
    except Exception as e:
        return e

def get_price_targets(ticker):
    try:
        targets = finviz.get_analyst_price_targets(ticker)
        targets = pd.DataFrame(targets)
        targets.columns = ['Date', 'Category', 'Analyst', 'Rating', 'Price From', 'Price To']
        targets = targets.set_index('Date')
        return targets
    except Exception as e:
        return e

print ('Fundamental Ratios: ')
print(get_fundamentals(symbol))

print ('\nRecent News: ')
print(get_news(symbol))

print ('\nRecent Insider Trades: ')
print(get_insider(symbol))

print ('\nAnalyst Price Targets: ')
print(get_price_targets(symbol))