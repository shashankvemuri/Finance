import smtplib
import datetime
import numpy as np
import pandas as pd
from email.mime.text import MIMEText
from yahoo_fin import stock_info as si
from pandas_datareader import DataReader
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import talib

# Define list of stocks
stock_list = ['AAPL', 'MSFT', 'AMZN']

# for the tradingview recommendation 
# options are: '1m', '5m', '15m', '1h', '4h', '1D', '1W', '1M
interval = "1M"

# Chromedriver Path
path = '/Users/shashank/Documents/Code/Python/Finance/chromedriver.exe' 

# Chromedriver Options
options = Options()
options.add_argument("--headless")
webdriver = webdriver.Chrome(executable_path=path, options=options)

# Define start and end dates
start = datetime.datetime.now() - datetime.timedelta(days=365)
end = datetime.datetime.now()

def sendMessage(text):
    message = text

    email = ""
    pas = ""
    sms_gateway = ''
    smtp = "smtp.gmail.com" 
    port = 587
    
    server = smtplib.SMTP(smtp,port)
    server.starttls()
    server.login(email,pas)

    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = sms_gateway
    msg['Subject'] = "Stock Data\n"
    body = "{}\n".format(message)
    msg.attach(MIMEText(body, 'plain'))

    sms = msg.as_string()

    server.sendmail(email,sms_gateway,sms)
    
    server.quit()
    
    print ('done')

def getData(list_of_stocks):
    for stock in list_of_stocks:
        df = DataReader(stock, 'yahoo', start, end)
        print (stock)
        
        # Current Price 
        price = si.get_live_price('{}'.format(stock))
        price = round(price, 2)
        
        # Sharpe Ratio
        x = 5000
        y = (x)
            
        stock_df = df
        stock_df['Norm return'] = stock_df['Adj Close'] / stock_df.iloc[0]['Adj Close']
         
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
        A_Sharpe_Ratio = (252**0.5) * Sharpe_Ratio        
        A_Sharpe_Ratio = round(A_Sharpe_Ratio, 2)
        
        # News Sentiment 
        finwiz_url = 'https://finviz.com/quote.ashx?t='
        news_tables = {}
        
        url = finwiz_url + stock
        req = Request(url=url,headers={'user-agent': 'my-app/0.0.1'}) 
        response = urlopen(req)    
        html = BeautifulSoup(response, features="lxml")
        news_table = html.find(id='news-table')
        news_tables[stock] = news_table
        
        parsed_news = []
        
        # Iterate through the news
        for file_name, news_table in news_tables.items():
            for x in news_table.findAll('tr'):
                text = x.a.get_text() 
                date_scrape = x.td.text.split()
        
                if len(date_scrape) == 1:
                    time = date_scrape[0]
                    
                else:
                    date = date_scrape[0]
                    time = date_scrape[1]
        
                ticker = file_name.split('_')[0]
                
                parsed_news.append([ticker, date, time, text])
                
        vader = SentimentIntensityAnalyzer()
        
        columns = ['ticker', 'date', 'time', 'headline']
        dataframe = pd.DataFrame(parsed_news, columns=columns)
        scores = dataframe['headline'].apply(vader.polarity_scores).tolist()
        
        scores_df = pd.DataFrame(scores)
        dataframe = dataframe.join(scores_df, rsuffix='_right')
        
        dataframe['date'] = pd.to_datetime(dataframe.date).dt.date
        dataframe = dataframe.set_index('ticker')
        
        sentiment = round(dataframe['compound'].mean(), 2)
        
        # TradingView Recommendation        
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
        
            signal = analysis[0]
            
        except:
            signal = 'None'
        
        # Beta
        df = DataReader(stock,'yahoo',start, end)
        dfb = DataReader('^GSPC','yahoo',start, end)
        
        rts = df.resample('M').last()
        rbts = dfb.resample('M').last()
        dfsm = pd.DataFrame({'s_adjclose' : rts['Adj Close'],
                                'b_adjclose' : rbts['Adj Close']},
                                index=rts.index)
        
        
        dfsm[['s_returns','b_returns']] = dfsm[['s_adjclose','b_adjclose']]/\
            dfsm[['s_adjclose','b_adjclose']].shift(1) -1
        dfsm = dfsm.dropna()
        covmat = np.cov(dfsm["s_returns"],dfsm["b_returns"])
                
        beta = covmat[0,1]/covmat[1,1] 
        beta = round(beta, 2)
        
        # Relative Strength Index
        df["rsi"] = talib.RSI(df["Close"])
        values = df["rsi"].tail(14)
        value = values.mean()
        rsi = round(value, 2)

        output = ("\nTicker: " + str(stock) + "\nCurrent Price : " + str(price) + "\nSharpe Ratio: " + str(A_Sharpe_Ratio) + "\nNews Sentiment: " + str(sentiment) + "\nTradingView Rec for {}: ".format(interval) + str(signal) + "\nRelative Strength Index: " + str(rsi) + "\nBeta Value for 1 Year: " + str(beta))
        sendMessage(output)

if __name__ == '__main__':
    getData(stock_list)