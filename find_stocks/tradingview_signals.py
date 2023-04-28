# Import Dependencies
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import datetime
from yahoo_fin import stock_info as si

# Set pandas option to display all rows
pd.set_option('display.max_rows', None)

# Set interval to get trading signals for
interval = '1m'

# Set chrome options
options = Options()
options.add_argument("--headless")  # To run the script in background
options.add_argument('window-size=1200x600')
webdriver = webdriver.Chrome(executable_path='chromedriver', options=options)

# List of tickers to get trading signals for
tickers = ['SCHB', 'AAPL', 'AMZN', 'TSLA', 'AMD', 'MSFT', 'NFLX']

# Initialize empty lists to store trading signals and other data
signals = []
sells = []
buys = []
neutrals = []
valid_tickers = []
prices = []

# Get today's date for file naming
today = datetime.date.today()

# Loop over the tickers to get the trading signals
for ticker in tickers:
    try:
        # Declare empty list to store analysis data
        analysis = []

        # Open tradingview's site
        webdriver.get(f"https://s.tradingview.com/embed-widget/technical-analysis/?locale=en#%7B%22interval%22%3A%22{interval}%22%2C%22width%22%3A%22100%25%22%2C%22isTransparent%22%3Afalse%2C%22height%22%3A%22100%25%22%2C%22symbol%22%3A%22{ticker}%22%2C%22showIntervalTabs%22%3Atrue%2C%22colorTheme%22%3A%22dark%22%2C%22utm_medium%22%3A%22widget_new%22%2C%22utm_campaign%22%3A%22technical-analysis%22%7D")
        webdriver.refresh()

        # Wait for site to load elements
        while len(webdriver.find_elements_by_class_name("speedometerSignal-pyzN--tL")) == 0:
            sleep(0.1)

        # Get recommendation
        recommendation_element = webdriver.find_element_by_class_name("speedometerSignal-pyzN--tL")
        analysis.append(recommendation_element.get_attribute('innerHTML'))

        # Get Sell, Neutral and Buy counter values
        counter_elements = webdriver.find_elements_by_class_name("counterNumber-3l14ys0C")
        analysis.append(int(counter_elements[0].get_attribute('innerHTML')))
        analysis.append(int(counter_elements[1].get_attribute('innerHTML')))
        analysis.append(int(counter_elements[2].get_attribute('innerHTML')))

        # Store the trading signals, price, and ticker name in the respective lists
        last_analysis = analysis
        signal = last_analysis[0]
        num_sell = float(last_analysis[1])
        num_neutral = float(last_analysis[2])
        num_buy = float(last_analysis[3])
        price = round(si.get_live_price(ticker), 2)

        signals.append(signal)
        neutrals.append(num_neutral)
        buys.append(num_buy)
        sells.append(num_sell)
        valid_tickers.append(ticker)
        prices.append(price)

        print(f"{ticker} has an overall recommendation of {signal}")
        
    except:
        continue
    
# Create dataframe, export, and print
dataframe = pd.DataFrame(list(zip(valid_tickers, prices, signals, buys, sells, neutrals)), columns =['Tickers', 'Current Price', 'Signals', 'Buys', 'Sells', 'Neutrals'])
dataframe = dataframe.set_index('Tickers')
dataframe = dataframe.sort_values('Signals', ascending=False)
dataframe.to_csv(f'{today}_{interval}.csv')
print (dataframe.head())