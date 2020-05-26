import requests
import pandas as pd

NetCurrentAssetValueperShare = {}

querytickers = requests.get(f'https://financialmodelingprep.com/api/v3/search?query=&limit=1000&exchange=NASDAQ')
querytickers = querytickers.json()

list_500 = querytickers
stocks = []
count = 0
for item in list_500:
    count = count +1
    #Stop after storing 50 stocks
    if count < 500:
        stocks.append(item['symbol'])

for company in stocks:
    Balance_Sheet = requests.get(f'https://financialmodelingprep.com/api/v3/financials/balance-sheet-statement/{company}?period=quarter')

    Balance_Sheet = Balance_Sheet.json()
    try:
        total_current_assets = float(Balance_Sheet['financials'][0]['Total current assets'])
        total_liabilities = float(Balance_Sheet['financials'][0]['Total liabilities'])
        sharesnumber = requests.get(f'https://financialmodelingprep.com/api/v3/enterprise-value/{company}')
        sharesnumber = sharesnumber.json()
        sharesnumber = float(sharesnumber['enterpriseValues'][0]['Number of Shares'])
       
        NCAVPS = (total_current_assets-total_liabilities)/sharesnumber
        
        price = float(sharesnumber['enterpriseValues'][0]['Stock Price'])
        #only companies where NCAVPS is below the stock price
        if NCAVPS < 0.67 * price:
            NetCurrentAssetValueperShare[company] = NCAVPS
    except:
        pass
    
    
print (NetCurrentAssetValueperShare)
