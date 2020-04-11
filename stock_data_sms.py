import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from yahoo_fin import stock_info as si      
import pandas as pd
from pandas_datareader import DataReader
import numpy as np
import datetime
import pprint

app = Flask(__name__)


@app.route('/sms', methods = ['POST'])
def sms(): 
    number = request.form['From']
    message_body = request.form['Body']
    resp = MessagingResponse()
    
    stock = message_body
    start_date = datetime.datetime.now() - datetime.timedelta(days=365)
    end_date = datetime.date.today()
    
    # price 
    price = si.get_live_price('{}'.format(message_body))
    price = round(price, 2)
    
    # volatility, momentum, beta, alpha, r_squared
    df = DataReader(stock,'yahoo',start_date, end_date)
    dfb = DataReader('^GSPC','yahoo',start_date, end_date)
    
    
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
    
    #fundamental data
    fundamental_data = si.get_quote_table(stock)
    fundamental_data = pprint.pformat(fundamental_data)
    fundamental_data = fundamental_data.strip('{}')
    
    resp.message('{} has the following: \ncurrent price - {} \nbeta(1Y) - {} \nalpha(1Y) - {} \nvolatility(1Y) - {} \nmomentum(1Y) - {} \nsharpe ratio(1Y) - {} \n{}'.format(message_body, price, beta, alpha, volatility, momentum, A_Sharpe_Ratio, fundamental_data))
    return str(resp)

if __name__ == "__main__":
    app.run(port=5000, debug=True)