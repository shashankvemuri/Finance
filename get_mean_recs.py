import csv
from datetime import datetime
import pickle
import bs4 as bs
import pandas as pd 
from yahoo_fin import stock_info as si 
import requests

tickers = pd.read_csv('all_tickers.csv')['Symbol']
tickers = tickers.values.tolist()
tickers = tickers[4002:]
tickers = [item.replace(".", "-") for item in tickers]

get_date = lambda : datetime.utcnow().strftime('%d-%m-%Y')

lhs_url = 'https://query2.finance.yahoo.com/v10/finance/quoteSummary/'
rhs_url = '?formatted=true&crumb=swg7qs5y9UP&lang=en-US&region=US&' \
          'modules=upgradeDowngradeHistory,recommendationTrend,' \
          'financialData,earningsHistory,earningsTrend,industryTrend&' \
          'corsDomain=finance.yahoo.com'

def get_mean_rec(ticker):
    url =  lhs_url + ticker + rhs_url
    r = requests.get(url)
    if not r.ok:
        return 6
    try:
        result = r.json()['quoteSummary']['result'][0]
        return result['financialData']['recommendationMean']['fmt']
    except:
        return 6

def read_from_csv(fn):
    with open(fn, 'r') as f:
        reader = csv.reader(f)
        for line in reader:
            for ticker in line:
                yield ticker

header = ['Company', 'Rec', 'Date']
def write_to_csv(fn, data):
    with open(fn, 'a') as f:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        for item in data:
            writer.writerow(item)

def assemble_dict(ticker):
    return {
        'ticker': ticker,
        'mean_rec': get_mean_rec(ticker),
        'utc_date': get_date()
    }

def main():
    #in_fn = input('ticker file: ')
    out_fn = input('output file: ')
    data = [assemble_dict(ticker) for ticker in tickers]
    write_to_csv(out_fn, data)

if __name__ == '__main__':
    main()
