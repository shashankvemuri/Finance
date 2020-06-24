import talib
import pickle
import datetime
import requests
import time as t
import bs4 as bs
import pandas as pd
import numpy as np 
from bs4 import BeautifulSoup
from pandas import ExcelWriter
from yahoo_fin import stock_info as si
from pandas_datareader import DataReader
from urllib.request import urlopen, Request
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def save_spx_tickers():
    resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class':'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.find_all('td') [0].text.strip()
        tickers.append(ticker)
        
    with open('spxTickers.pickle', 'wb') as f:
            pickle.dump(tickers, f)       
    return tickers
        
stocklist = save_spx_tickers()

# Make the ticker symbols readable by Yahoo Finance
stocklist = [item.replace(".", "-") for item in stocklist]

mylist = []
today = datetime.date.today()
mylist.append(today)
today = mylist[0]

exportList = pd.DataFrame(columns=["Stock", "Price", "RSI", "Sharpe Ratio", "News Sentiment", "Recommendation", "Alpha", "Volatility", "Beta", "Volume"])
otherList = pd.DataFrame(columns=["Stock", "Price", "RSI", "Sharpe Ratio", "News Sentiment", "Recommendation", "Alpha", "Volatility", "Beta", "Volume", "Failed"])

for stock in stocklist:
    t.sleep(3)
    
    print ("\npulling {}".format(stock))
    # rsi value
    start_date = datetime.datetime.now() - datetime.timedelta(days=365)
    end_date = datetime.date.today()    
    
    try:
        #get historical data 
        df = DataReader(stock, 'yahoo', start=start_date, end=end_date)
        
        #current price
        price = si.get_live_price(stock)
        
        #RSI 
        df["rsi"] = talib.RSI(df["Close"])
        rsi = df["rsi"].tail(14).mean()
        
        # Sharpe Ratio
        x = 5000
        y = (x)
    
        stock_df = df
        stock_df['Norm return'] = stock_df['Adj Close'] / \
            stock_df.iloc[0]['Adj Close']
    
        allocation = float(x/y)
        stock_df['Allocation'] = stock_df['Norm return'] * allocation
    
        stock_df['Position'] = stock_df['Allocation'] * x
        pos = [df['Position']]
        val = pd.concat(pos, axis=1)
        val.columns = ['WMT Pos']
        val['Total Pos'] = val.sum(axis=1)
    
        val.tail(1)    
        val['Daily Return'] = val['Total Pos'].pct_change(1)
    
        Sharpe_Ratio = val['Daily Return'].mean() / val['Daily Return'].std()    
        sharpe_ratio = (252**0.5) * Sharpe_Ratio    
        sharpe_ratio = round(sharpe_ratio, 2)
        
        #news sentiment 
        finwiz_url = 'https://finviz.com/quote.ashx?t='
        news_tables = {}
        
        url = finwiz_url + stock
        req = Request(url=url,headers={'user-agent': 'my-app/0.0.1'}) 
        resp = urlopen(req)    
        html = BeautifulSoup(resp, features="lxml")
        news_table = html.find(id='news-table')
        news_tables[stock] = news_table
        
        try:
            df = news_tables[stock]
            df_tr = df.findAll('tr')
            
            for i, table_row in enumerate(df_tr):
                a_text = table_row.a.text
                td_text = table_row.td.text
                td_text = td_text.strip()
                #print(a_text,'(',td_text,')')
                if i == 3:
                    break
        except KeyError:
            pass
    
        parsed_news = []
        for file_name, news_table in news_tables.items():
            for x in news_table.findAll('tr'):
                text = x.a.get_text() 
                date_scrape = x.td.text.split()
        
                if len(date_scrape) == 1:
                    time = date_scrape[0]
                    
                else:
                    date = date_scrape[0]
                    time = date_scrape[1]
        
                stock = file_name.split('_')[0]
                
                parsed_news.append([stock, date, time, text])
    
        analyzer = SentimentIntensityAnalyzer()
        
        columns = ['stock', 'Date', 'Time', 'Headline']
        news = pd.DataFrame(parsed_news, columns=columns)
        scores = news['Headline'].apply(analyzer.polarity_scores).tolist()
        
        df_scores = pd.DataFrame(scores)
        news = news.join(df_scores, rsuffix='_right')
        
        news['Date'] = pd.to_datetime(news.Date).dt.date
        
        unique_stock = news['stock'].unique().tolist()
        news_dict = {name: news.loc[news['stock'] == name] for name in unique_stock}
        
        dataframe = news_dict[stock]
        dataframe = dataframe.set_index('stock')
        dataframe = dataframe.drop(columns = ['Headline'])
        sentiment_value = round(dataframe['compound'].mean(), 2)
        
        
        #Recommendation
        lhs_url = 'https://query2.finance.yahoo.com/v10/finance/quoteSummary/'
        rhs_url = '?formatted=true&crumb=swg7qs5y9UP&lang=en-US&region=US&' \
                  'modules=upgradeDowngradeHistory,recommendationTrend,' \
                  'financialData,earningsHistory,earningsTrend,industryTrend&' \
                  'corsDomain=finance.yahoo.com'
    
        url = lhs_url + stock + rhs_url
        r = requests.get(url)
        if not r.ok:
            rec_val = 6
        try:
            result = r.json()['quoteSummary']['result'][0]
            rec_val = result['financialData']['recommendationMean']['fmt']
        except:
            rec_val = 6
        
        #alpha, volatility, beta
        df = DataReader(stock, 'yahoo', start_date, end_date)
        dfb = DataReader('^GSPC', 'yahoo', start_date, end_date)
    
        rts = df.resample('M').last()
        rbts = dfb.resample('M').last()
        dfsm = pd.DataFrame({'s_adjclose': rts['Adj Close'],
                             'b_adjclose': rbts['Adj Close']},
                            index=rts.index)
    
        dfsm[['s_returns', 'b_returns']] = dfsm[['s_adjclose', 'b_adjclose']] /\
            dfsm[['s_adjclose', 'b_adjclose']].shift(1) - 1
        dfsm = dfsm.dropna()
        covmat = np.cov(dfsm["s_returns"], dfsm["b_returns"])
    
        beta = covmat[0, 1]/covmat[1, 1]
    
        alpha = np.mean(dfsm["s_returns"])-beta*np.mean(dfsm["b_returns"])
    
        ypred = alpha + beta * dfsm["b_returns"]
        SS_res = np.sum(np.power(ypred-dfsm["s_returns"], 2))
        SS_tot = covmat[0, 0]*(len(dfsm)-1)  # SS_tot is sample_variance*(n-1)
        r_squared = 1. - SS_res/SS_tot
    
        volatility = np.sqrt(covmat[0, 0])
        momentum = np.prod(1+dfsm["s_returns"].tail(12).values) - 1
    
        prd = 12.
        alpha = alpha*prd
        volatility = volatility*np.sqrt(prd)
    
        beta = round(beta, 2)
        alpha = round(alpha, 2)
        volatility = round(volatility, 2)            
        
        #volume
        volume = df.Volume
        volume = volume.tail(60).mean()
        
        # Condition 1: Price is greater than 1 dollar
        if(price > 2):
            condition_1 = True
        else:
            condition_1 = False
        
        # Condition 2: RSI lower than 45
        if(rsi < 45):
            condition_2 = True
        else:
            condition_2 = False
        
        # Condition 3: Sharpe Ratio greater than 1.5
        if(sharpe_ratio > 1.5):
            condition_3 = True
        else:
            condition_3 = False
        
        # Condition 4: News sentiment greater than 0.05
        if(sentiment_value > 0.05):
            condition_4 = True
        else:
            condition_4 = False
        
        # Condition 5: Recommendation value less than 3
        if(float(rec_val) <= 3):
            condition_5 = True
        else:
            condition_5 = False
        
        # Condition 6: Alpha greater than 0.05
        if(alpha > 0.05):
            condition_6 = True
        else:
            condition_6 = False
        
        # Condition 7: Beta less than 3 and greater than 0.5
        if(beta < 3 and beta > 0.5):
            condition_7 = True
        else:
            condition_7 = False
        
        # Condition 8: Volatility less than 0.3
        if(volatility < 0.3):
            condition_8 = True
        else:
            condition_8 = False
            
        # Condition 9: Volume greater than 500,000
        if(volume > 500,000):
            condition_9 = True
        else:
            condition_9 = False
    
        if(condition_1 and condition_2 and condition_3 and condition_4 and condition_5 and condition_6 and condition_7 and condition_8):            
            exportList = exportList.append({'Stock': stock, "Price": price, "RSI": rsi, "Sharpe Ratio": sharpe_ratio, "News Sentiment": sentiment_value, "Recommendation": rec_val, "Alpha": alpha, "Volatility": volatility, "Beta": beta, "Volume": volume}, ignore_index=True)
            print (stock + " made the requirements")
        
        else:
            conditions = {'condition_1': condition_1, 'condition_2': condition_2, 'condition_3': condition_3, 'condition_4': condition_4, 'condition_5': condition_5, 'condition_6': condition_6, 'condition_7': condition_7, 'condition_8': condition_8, 'condition_9': condition_9}
            
            false = []
            for condition in conditions: 
                if conditions[condition] == False: 
                    false.append(condition)
                else:
                    pass
                
            print (stock + " did not make the requirements because of: ")        
            for value in false: 
                print (value)
                
            otherList = otherList.append({'Stock': stock, "Price": price, "RSI": rsi, "Sharpe Ratio": sharpe_ratio, "News Sentiment": sentiment_value, "Recommendation": rec_val, "Alpha": alpha, "Volatility": volatility, "Beta": beta, "Volume": volume, "Failed": false}, ignore_index=True)
    except Exception as e: 
        print (e)
        print (f"could not get data on {stock}")
        pass

#print(exportList)
writer = ExcelWriter('/Users/shashank/Documents/GitHub/Code/data-screener-output/Export-Output_{}.xlsx'.format(today))
exportList.to_excel(writer, "Sheet1")
writer.save()

writer = ExcelWriter('/Users/shashank/Documents/GitHub/Code/data-screener-output/Other-Output_{}.xlsx'.format(today))
otherList.to_excel(writer, "Sheet1")
writer.save()
