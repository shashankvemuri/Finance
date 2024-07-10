# Importing necessary libraries
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from pandas_datareader import data as pdr
import yfinance as yf
import sys
import os
parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)
import tickers as ti
yf.pdr_override()

# Define stock tickers and time interval
tickers = ['DDOG', 'NVDA', 'PTON', 'RH', 'ROKU', 'SE', 'SQ', 'TSLA', 'TTD']
interval = '1D'

# Getting lists of tickers from NASDAQ, NYSE, and AMEX
nasdaq = ti.tickers_nasdaq()
nyse = ti.tickers_nyse()
amex = ti.tickers_amex()

# Define valid time intervals
type_intervals = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '1D', '1W', '1M']

# Set up Selenium WebDriver
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Helper function to parse recommendation data
def parse_recommendation(recommendation_elements, counter_elements, rec_index, sell_index, buy_index):
    rec = recommendation_elements[rec_index].get_attribute('innerHTML')
    sell_signals = int(counter_elements[sell_index].get_attribute('innerHTML'))
    neutral_signals = int(counter_elements[sell_index + 1].get_attribute('innerHTML'))
    buy_signals = int(counter_elements[buy_index].get_attribute('innerHTML'))
    return rec, sell_signals, neutral_signals, buy_signals

# Helper function to display recommendations
def display_recommendations(analysis):
    for key in analysis:
        print(f"\n{key} Recommendation: ")
        rec, sell, neutral, buy = analysis[key]
        print(f"Recommendation: {rec}")
        print(f"Sell Signals: {sell}")
        print(f"Neutral Signals: {neutral}")
        print(f"Buy Signals: {buy}")

# Helper function to scrape tables
def scrape_tables(html):
    tables = pd.read_html(html, attrs = {'class': 'table-hvDpy38G'})
    return tables[0], tables[1], tables[2]  # Oscillator, Moving Averages, and Pivots tables

# Helper function to print tables
def print_tables(oscillator_table, ma_table, pivots_table):
    print("\nOscillator Table:")
    print(oscillator_table)
    print("\nMoving Average Table:")
    print(ma_table)
    print("\nPivots Table:")
    print(pivots_table)

# Process each ticker
for ticker in tickers:
    try:
        # Determine the exchange of the ticker
        if ticker in nasdaq:
            exchange = 'NASDAQ'
        elif ticker in nyse:
            exchange = 'NYSE'
        elif ticker in amex:
            exchange = 'AMEX'
        else:
            print(f"Could not find the exchange for {ticker}")
            continue

        # Get the current price of the ticker
        df = pdr.get_data_yahoo(ticker)
        price = round(df["Adj Close"][-1], 2)

        # Open TradingView page for the ticker
        driver.get(f"https://www.tradingview.com/symbols/{exchange}-{ticker}/technicals")
        time.sleep(1)

        # Display ticker, interval, and price information
        print('\nTicker: ' + ticker)
        print('Interval: ' + interval)
        print('Price: ' + str(price))

        # Switch to the specified interval on TradingView page
        for type_interval in type_intervals:
            if interval == type_interval:
                # n = type_intervals.index(type_interval)
                element = driver.find_element(By.XPATH, f'//*[@id="{interval}"]')
                # print (len(element))
                element.click()
                break

        time.sleep(1)

        # Scrape and display Overall, Oscillator, and Moving Average Recommendations
        recommendation_elements = driver.find_elements(By.CLASS_NAME, "speedometerText-Tat_6ZmA")
        counter_elements = driver.find_elements(By.CLASS_NAME, "counterNumber-kg4MJrFB")
        analysis = {
            'Overall': parse_recommendation(recommendation_elements, counter_elements, 1, 3, 5),
            'Oscillator': parse_recommendation(recommendation_elements, counter_elements, 0, 0, 2),
            'Moving Average': parse_recommendation(recommendation_elements, counter_elements, 2, 6, 8)
        }
        display_recommendations(analysis)

        # Scrape and display tables for Oscillator, Moving Averages, and Pivots
        html = driver.page_source
        oscillator_table, ma_table, pivots_table = scrape_tables(html)
        print_tables(oscillator_table, ma_table, pivots_table)

    except Exception as e:
        print(f'Could not retrieve stats for {ticker} due to {e}')

# Close the WebDriver
driver.close()