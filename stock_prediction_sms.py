import numpy as np
import datetime
import smtplib
import os
from selenium import webdriver
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import preprocessing
from pandas_datareader import DataReader
from yahoo_fin import stock_info as si      
import pandas as pd

pd.set_option('display.max_rows', None)

def getStocks(n):
    driver = webdriver.Chrome(executable_path='/Users/shashank/Documents/Code/Python/Finance/chromedriver.exe')
    url = "https://finance.yahoo.com/screener/predefined/aggressive_small_caps?offset=0&count=202"
    driver.get(url)
    stock_list = []
    n += 1
    for i in range(1, n):
        driver.implicitly_wait(10)
        ticker = driver.find_element_by_xpath('//*[@id = "scr-res-table"]/div[1]/table/tbody/tr[' + str(i) + ']/td[1]/a')
        stock_list.append(ticker.text)

    number = 0
    for i in stock_list:
        predictData(i, 5)
        number += 1
    
def sendMessage(text):

    message = text
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

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
    msg['Subject'] = "Stocks\n"
    body = "{}\n".format(message)
    msg.attach(MIMEText(body, 'plain'))

    sms = msg.as_string()

    server.sendmail(email,sms_gateway,sms)
    
    server.quit()
    
    print ('sent')
    

stock_list = []
predictions = []
confidence = []
error_list = []

def predictData(stock, days):
    stock_list.append(stock)

    start = datetime.datetime.now() - datetime.timedelta(days=365)
    end = datetime.datetime.now()

    df = DataReader(stock, 'yahoo', start, end)
    if os.path.exists('./Exports'):
        csv_name = ('Exports/' + stock + '_Export.csv')
    else:
        os.mkdir("Exports")
        csv_name = ('Exports/' + stock + '_Export.csv')
        df.to_csv(csv_name)
        df['Prediction'] = df['Close'].shift(-1)
        df.dropna(inplace=True)

    forecast_time = int(days)
    
    df['Prediction'] = df['Close'].shift(-1)
    df1 = df['Prediction']
    array = np.array(df['Close'])
    array1 = np.array(df1)
    array = array.reshape(-1, 1)
    array1 = array1.reshape(-1, 1)
    
    X = array
    Y = array1
    X = np.nan_to_num(X)
    Y = np.nan_to_num(Y)
    X = preprocessing.scale(X)
    X_prediction = X[-forecast_time:]
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, train_size = 0.8, test_size=0.2)

    clf = LinearRegression()
    clf.fit(X_train, Y_train)
    prediction = (clf.predict(X_prediction))
    
    prediction = np.around(prediction, decimals = 3)

    print (stock)
    last_row = df.tail(1)
    last_row = last_row.reset_index()
    last_row = last_row['Close']
    last_row = last_row.to_string(index=False)
    print('Close: {}'.format(last_row))
    print ('-'*80)
        
    lr = LinearRegression()
    lr.fit(X_train, Y_train)    
    lr_confidence = lr.score(X_test, Y_test)
    lr_confidence = round(lr_confidence, 2)

    # price 
    price = si.get_live_price('{}'.format(stock))
    price = round(price, 2)
    
    # volatility, momentum, beta, alpha, r_squared
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
    
    alpha= np.mean(dfsm["s_returns"])-beta*np.mean(dfsm["b_returns"])
    
    ypred = alpha + beta * dfsm["b_returns"]
    SS_res = np.sum(np.power(ypred-dfsm["s_returns"],2))
    SS_tot = covmat[0,0]*(len(dfsm)-1) # SS_tot is sample_variance*(n-1)
    r_squared = 1. - SS_res/SS_tot
    
    
    volatility = np.sqrt(covmat[0,0])
    momentum = np.prod(1+dfsm["s_returns"].tail(12).values) -1
    
    
    prd = 12. 
    alpha = alpha*prd
    volatility = volatility*np.sqrt(prd)
    
    beta = round(beta, 2)
    alpha = round(alpha, 2)
    r_squared = round(r_squared, 2)
    volatility = round(volatility, 2)
    momentum = round(momentum, 2)
    
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
    
    difference = float(prediction[4]) - float(last_row)
    change = float(difference)/float(last_row)
    predictions.append(change)
    
    confidence.append(lr_confidence)
    
    error = 1 - float(lr_confidence)
    error_list.append(error)
    
    if (float(prediction[4]) > (float(last_row)) and (float(lr_confidence)) > 0.8):
        output = ("\nStock: " + str(stock) + "\nLast Close: " + str(last_row) + "\nPrediction in 1 Day: " + str(prediction[0]) + "\nPrediction in 5 Days: " + str(prediction[4]) + "\nConfidence: " + str(lr_confidence) + "\nCurrent Price : " + str(price) + "\n\nStock Data: " + "\nBeta: " + str(beta) + "\nAlpha: " + str(alpha) + "\nSharpe Ratio: " + str(A_Sharpe_Ratio) + "\nVolatility: " + str(volatility) + "\nMomentum: " + str(momentum))
        sendMessage(output)

if __name__ == '__main__':
    getStocks(1)
    