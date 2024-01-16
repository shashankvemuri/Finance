# Import Dependencies
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime
import pandas_datareader.data as pdr

# Set pandas option and interval
pd.set_option('display.max_rows', None)
interval = '1m'

# Initialize WebDriver for Chrome
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# List of tickers and initialization of lists for data
tickers = ['SCHB', 'AAPL', 'AMZN', 'TSLA', 'AMD', 'MSFT', 'NFLX']
signals, sells, buys, neutrals, valid_tickers, prices = [], [], [], [], [], []

# Today's date for file naming
today = datetime.date.today()

# Process each ticker for trading signals
for ticker in tickers:
    try:
        driver.get(f"https://s.tradingview.com/embed-widget/technical-analysis/?symbol={ticker}&interval={interval}")
        driver.refresh()
        sleep(2)  # Adjust the sleep time if necessary

        # Extract recommendation and counter values
        recommendation = driver.find_element_by_class_name("speedometerSignal-pyzN--tL").text
        counters = [element.text for element in driver.find_elements_by_class_name("counterNumber-3l14ys0C")]
        
        # Append data to lists
        signals.append(recommendation)
        sells.append(float(counters[0]))
        neutrals.append(float(counters[1]))
        buys.append(float(counters[2]))
        price = pdr.get_data_yahoo(ticker)['Adj Close'][-1]
        prices.append(price)
        valid_tickers.append(ticker)

        print(f"{ticker} recommendation: {recommendation}")

    except Exception as e:
        print(f"Error with {ticker}: {e}")

# Close WebDriver
driver.close()

# Create and print DataFrame
dataframe = pd.DataFrame({'Tickers': valid_tickers, 'Current Price': prices, 'Signals': signals, 'Buys': buys, 'Sells': sells, 'Neutrals': neutrals}).set_index('Tickers')
dataframe.sort_values('Signals', ascending=False, inplace=True)
dataframe.to_csv(f'{today}_{interval}.csv')
print(dataframe)