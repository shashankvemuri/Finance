import yfinance as yf
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates

def view_stock_returns(symbol, num_years):
    # Fetch stock data for the given number of years
    start_date = dt.date.today() - dt.timedelta(days=365 * num_years)
    end_date = dt.date.today()
    dataset = yf.download(symbol, start_date, end_date)
    
    # Plot Adjusted Close Price over time
    plt.figure(figsize=(15, 10))
    plt.plot(dataset['Adj Close'], label='Adj Close')
    plt.title(f'{symbol} Closing Price Chart')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.grid(True)
    plt.legend()
    plt.show()

    # Monthly Returns Analysis
    monthly_dataset = dataset.asfreq('BM')
    monthly_dataset['Returns'] = dataset['Adj Close'].pct_change().dropna()
    monthly_dataset['Month_Name'] = monthly_dataset.index.strftime('%b-%Y')
    monthly_dataset['ReturnsPositive'] = monthly_dataset['Returns'] > 0
    colors = monthly_dataset['ReturnsPositive'].map({True: 'g', False: 'r'})

    plt.figure(figsize=(15, 10))
    monthly_dataset['Returns'].plot(kind='bar', color=colors)
    plt.xticks(monthly_dataset.index, monthly_dataset['Month_Name'], rotation=45)
    plt.title('Monthly Returns')
    plt.xlabel('Month')
    plt.ylabel('Returns')
    plt.show()

    # Yearly Returns Analysis
    yearly_dataset = dataset.asfreq('BY')
    yearly_dataset['Returns'] = dataset['Adj Close'].pct_change().dropna()
    yearly_dataset['ReturnsPositive'] = yearly_dataset['Returns'] > 0
    colors_year = yearly_dataset['ReturnsPositive'].map({True: 'g', False: 'r'})

    plt.figure(figsize=(15, 10))
    plt.bar(yearly_dataset.index.year, yearly_dataset['Returns'], color=colors_year)
    plt.title('Yearly Returns')
    plt.xlabel('Year')
    plt.ylabel('Returns')
    plt.show()

# Example Usage
symbol = 'AAPL'
num_years = 5
view_stock_returns(symbol, num_years)