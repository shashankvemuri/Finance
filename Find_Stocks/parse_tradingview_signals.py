# imports 
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import datetime
from yahoo_fin import stock_info as si

pd.set_option('display.max_rows', None)

interval = '1m'

options = Options()
options.add_argument("--headless")
options.add_argument('window-size=1200x600')
webdriver = webdriver.Chrome(executable_path='/Users/shashank/Documents/Code/Python/Finance/chromedriver', options = options)

tickers = ['SCHB', 'AAPL', 'AMZN', 'TSLA', 'AMD', 'MSFT', 'NFLX']

mylist = []
today = datetime.date.today()
mylist.append(today)
today = mylist[0]

signals = []
sells = []
buys = []
neutrals = []
valid_tickers = []
prices = []

for ticker in tickers:
    try:
        #Declare variable
        analysis = []
        
        #Open tradingview's site
        webdriver.get("https://s.tradingview.com/embed-widget/technical-analysis/?locale=en#%7B%22interval%22%3A%22{}%22%2C%22width%22%3A%22100%25%22%2C%22isTransparent%22%3Afalse%2C%22height%22%3A%22100%25%22%2C%22symbol%22%3A%22{}%22%2C%22showIntervalTabs%22%3Atrue%2C%22colorTheme%22%3A%22dark%22%2C%22utm_medium%22%3A%22widget_new%22%2C%22utm_campaign%22%3A%22technical-analysis%22%7D".format(interval, ticker))
        webdriver.refresh()
        
        #Wait for site to load elements
        while len(webdriver.find_elements_by_class_name("speedometerSignal-pyzN--tL")) == 0:
            sleep(0.1)
        
        #Recommendation
        recommendation_element = webdriver.find_element_by_class_name("speedometerSignal-pyzN--tL")
        analysis.append(recommendation_element.get_attribute('innerHTML'))
        
        #Counters
        counter_elements = webdriver.find_elements_by_class_name("counterNumber-3l14ys0C")
        
        #Sell
        analysis.append(int(counter_elements[0].get_attribute('innerHTML')))
        
        #Neutral
        analysis.append(int(counter_elements[1].get_attribute('innerHTML')))
        
        #Buy
        analysis.append(int(counter_elements[2].get_attribute('innerHTML')))
        
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
        
        print (f'{ticker} has an overall recommendation of {signal}')
        print ('-'*60)
        
    except:
        continue
    
dataframe = pd.DataFrame(list(zip(valid_tickers, prices, signals, buys, sells, neutrals)), columns =['Tickers', 'Current Price', 'Signals', 'Buys', 'Sells', 'Neutrals'])
dataframe = dataframe.set_index('Tickers')
dataframe.to_csv(f'/Users/shashank/Documents/Code/Python/Outputs/tradingview/{today}_{interval}.csv')

dataframe = pd.read_csv(f'/Users/shashank/Documents/Code/Python/Outputs/tradingview/{today}_{interval}.csv', index_col=0)
# dataframe = dataframe.drop(columns = 'Unnamed: 0')
dataframe = dataframe.sort_values('Signals', ascending=False)
print (dataframe.head(15))
