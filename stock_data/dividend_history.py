from datetime import datetime, timedelta
import time
import requests
import pandas as pd
from lxml import html

# Function to convert datetime to string format for URL
def format_date(date_datetime):
    date_mktime = time.mktime(date_datetime.timetuple())
    return str(int(date_mktime))

# Function to construct URL for Yahoo Finance dividend history
def subdomain(symbol, start, end):
    format_url = f"{symbol}/history?period1={start}&period2={end}"
    tail_url = "&interval=div%7Csplit&filter=div&frequency=1d"
    return format_url + tail_url

# Function to define HTTP headers for request
def header(subdomain):
    hdrs = {"authority": "finance.yahoo.com", "method": "GET", "path": subdomain,
            "scheme": "https", "accept": "text/html,application/xhtml+xml",
            "accept-encoding": "gzip, deflate, br", "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache", "cookie": "cookies", "dnt": "1", "pragma": "no-cache",
            "sec-fetch-mode": "navigate", "sec-fetch-site": "same-origin", "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1", "user-agent": "Mozilla/5.0"}
    return hdrs

# Function to scrape dividend history page and return DataFrame
def scrape_page(url, header):
    page = requests.get(url, headers=header)
    element_html = html.fromstring(page.content)
    table = element_html.xpath('//table')[0]
    table_tree = html.tostring(table, method='xml')
    df = pd.read_html(table_tree)
    return df[0]

# Function to clean dividend data
def clean_dividends(symbol, dividends):
    dividends = dividends.drop(len(dividends) - 1)
    dividends = dividends.set_index('Date')['Dividends'].str.replace(r'\Dividend', '').astype(float)
    dividends.name = symbol
    return dividends

# Main script
if __name__ == '__main__':
    symbol = input("Enter a ticker: ").upper()
    start = format_date(datetime.today() - timedelta(days=9125))
    end = format_date(datetime.today())

    sub = subdomain(symbol, start, end)
    hdrs = header(sub)

    base_url = "https://finance.yahoo.com/quote/"
    url = base_url + sub
    dividends_df = scrape_page(url, hdrs)
    dividends = clean_dividends(symbol, dividends_df)

    print(dividends)