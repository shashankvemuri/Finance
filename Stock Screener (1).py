import datetime
import requests
import pandas as pd
from yahoo_fin import stock_info as si
from pandas_datareader import DataReader
import numpy as np
from pandas_datareader import data as pdr
import os
from pandas import ExcelWriter

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

start_date = datetime.date(2020, 2, 21)
end_date = datetime.date.today()

#tickers = pd.read_csv('all_recs(2).csv')['Company'].tolist()
tickers = si.tickers_nasdaq()

exportList = pd.DataFrame(columns=["Stock", "Price", "RS_Rating", "Sharpe Ratio", "Recommendation", "Alpha", "Volatility", "Beta",
                                   "Momentum", "Dividend", "Volume", "R-Squared"])  # "Market Cap", "PE Ratio", "Debt-Equity Ratio", "Current Ratio", "ROE"])
importList = pd.DataFrame(columns=["Stock", "Price", "RS_Rating", "Sharpe Ratio", "Recommendation", "Alpha", "Volatility", "Beta",
                                   "Momentum", "Dividend", "Volume", "R-Squared"])  # "Market Cap", "PE Ratio", "Debt-Equity Ratio", "Current Ratio", "ROE"])


for ticker in tickers:
    print('\nPulling {}'.format(ticker))

    lhs_url = 'https://query2.finance.yahoo.com/v10/finance/quoteSummary/'
    rhs_url = '?formatted=true&crumb=swg7qs5y9UP&lang=en-US&region=US&' \
              'modules=upgradeDowngradeHistory,recommendationTrend,' \
              'financialData,earningsHistory,earningsTrend,industryTrend&' \
              'corsDomain=finance.yahoo.com'

    url = lhs_url + ticker + rhs_url
    r = requests.get(url)
    if not r.ok:
        recommendation = 0
    try:
        result = r.json()['quoteSummary']['result'][0]
        recommendation = result['financialData']['recommendationMean']['fmt']
    except:
        recommendation = 0

    '''
    data = si.get_stats(('{}'.format(ticker)))
    data = data.set_index('Attribute')   
    data = data.drop(['Dividend Date 3', 'Ex-Dividend Date 4', 'Last Split Date 3', 'Fiscal Year Ends', 'Most Recent Quarter (mrq)', 'Last Split Factor 2'])
    
    data['Value'] = data['Value'].str.replace('K', '*1e3')
    data['Value'] = data['Value'].str.replace('M', '*1e6')
    data['Value'] = data['Value'].str.replace('B', '*1e9')
    data['Value'] = data['Value'].str.replace('T', '*1e12')
    data['Value'] = data['Value'].str.replace('%', '*1e-2')
    
    market_cap = data.iat[0,0]
    pe_ratio = data.iat[3, 0]
    ROE = data.iat[36, 0]
    debt_equity = data.iat[48,0]
    current_ratio = data.iat[49, 0]
    '''

    # price
    price = si.get_live_price('{}'.format(ticker))
    price = round(price, 2)

    # volatility, momentum, beta, alpha, r_squared
    df = DataReader(ticker, 'yahoo', start_date, end_date)
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
    r_squared = round(r_squared, 2)
    volatility = round(volatility, 2)
    momentum = round(momentum, 2)

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

    A_Sharpe_Ratio = (252**0.5) * Sharpe_Ratio

    A_Sharpe_Ratio = round(A_Sharpe_Ratio, 2)

    # earnings date, dividend, volume
    fundamental_data = si.get_quote_table(ticker)
    keys, values = zip(*fundamental_data.items())
    keys = list(keys)
    values = list(values)

    earnings_date = values[8]
    dividend = values[10]
    volume = values[16]

    # rsi value
    start = datetime.datetime.now() - datetime.timedelta(days=60)
    end = datetime.date.today()

    data = pdr.get_data_yahoo(ticker, start=start, end=end)

    rsi_period = 14
    chg = data['Close'].diff(1)
    gain = chg.mask(chg < 0, 0)
    data['gain'] = gain
    loss = chg.mask(chg > 0, 0)
    data['loss'] = loss
    avg_gain = gain.ewm(com=rsi_period - 1, min_periods=rsi_period).mean()
    avg_loss = loss.ewm(com=rsi_period - 1, min_periods=rsi_period).mean()
    data['avg_gain'] = avg_gain
    data['avg_loss'] = avg_loss
    rs = abs(avg_gain/avg_loss)
    rsi = 100-(100/(1+rs))
    rsi = rsi.reset_index()
    rsi = rsi.drop(columns=['Date'])
    rsi.columns = ['Value']

    rsi_mean = rsi['Value'].mean()

    try:
        # Condition 1: Price is greater than or equal to 1 dollar
        if(price >= 1):
            cond_1 = True
        else:
            cond_1 = False
        # Condition 2: RSI Value is greater than or equal to 70
        if(rsi_mean >= 70):
            cond_2 = True
        else:
            cond_2 = False
        # Condition 3: Sharpe Ratio is greater than or equal to 1.2
        if(A_Sharpe_Ratio >= 1.2):
            cond_3 = True
        else:
            cond_3 = False
        # Condition 4: Volatility is less than or equal to 0.10
        if(volatility <= 0.10):
            cond_4 = True
        else:
            cond_4 = False
        # Condition 5: Alpha is greater than or equal to 0.01
        if(alpha >= 0.01):
            cond_5 = True
        else:
            cond_5 = False
        # Condition 6: Momentum greater than or equal to 0.05
        if(momentum >= 0.05):
            cond_6 = True
        else:
            cond_6 = False
        # Condition 7: Beta is between 0.5 and 2.5
        if(beta >= 0.5 and beta <= 2.5):
            cond_7 = True
        else:
            cond_7 = False
        # Condition 8: Volume is greater than 20 million
        if(volume > 20000000):
            cond_8 = True
        else:
            cond_8 = False
        # Condition 9: Recommendation Value is greater than 3.5
        if(recommendation >= 3.5):
            cond_9 = True
        else:
            cond_9 = False
        '''
        #Condition 10: Stock is a Mid-Cap stock 
    	if(market_cap >= 2000000000):
    		cond_10=True
    	else:
    		cond_10=False
    	#Condition 11: PE Ratio between 10 and 25
    	if(pe_ratio >= 10 and pe_ratio <= 25):
    		cond_11=True
    	else:
    		cond_11=False
        #Condition 12: Debt Equity Ratio between 1.0 and 1.5
    	if(debt_equity >= 1.0 and debt_equity <= 1.5):
    		cond_12=True
    	else:
    		cond_12=False
        #Condition 13: Current Ratio between 1.2 and 2
    	if(current_ratio >= 1.2 and current_ratio <= 2):
    		cond_13=True
    	else:
    		cond_13=False
        #Condition 14: ROE between 0.09 and 0.2
    	if(ROE >= 0.09 and ROE <= 0.2):
    		cond_14=True
    	else:
    		cond_14=False
        '''
        if(cond_1 and cond_2 and cond_3 and cond_4 and cond_5 and cond_6 and cond_7 and cond_8 and cond_9):  # and cond_10 and cond_11 and cond_12 and cond_13 and cond_14):
            exportList = exportList.append({"Stock": ticker, "Price": price, "RS_Rating": rsi_mean, "Sharpe Ratio": A_Sharpe_Ratio, "Recommendation": recommendation, "Alpha": alpha, "Volatility": volatility, "Beta": beta, "Momentum": momentum,
                                            "Dividend": dividend, "Volume": volume, "R-Squared": r_squared}, ignore_index=True)  # "Market Cap": market_cap, "PE Ratio": pe_ratio, "Debt-Equity Ratio": debt_equity, "Current Ratio": current_ratio, "ROE": ROE}, ignore_index=True)
            print ('{} met the requirements'.format(ticker))
            
        else:
            importList = importList.append({"Stock": ticker, "Price": price, "RS_Rating": rsi_mean, "Sharpe Ratio": A_Sharpe_Ratio, "Recommendation": recommendation, "Alpha": alpha, "Volatility": volatility, "Beta": beta, "Momentum": momentum,
                                            "Dividend": dividend, "Volume": volume, "R-Squared": r_squared}, ignore_index=True)  # "Market Cap": market_cap, "PE Ratio": pe_ratio, "Debt-Equity Ratio": debt_equity, "Current Ratio": current_ratio, "ROE": ROE}, ignore_index=True)
            print("{} did not meet requirements".format(ticker))
    except:
        print("Could not fetch data for {}".format(ticker))

print(exportList)

filePath = r"/Users/shashank/Downloads/Code"

goodFile = os.path.dirname(filePath)+"/OwnScreenOutput.xlsx"
allFile = os.path.dirname(filePath)+"/AllOwnScreenOutput.xlsx"

writer = ExcelWriter(goodFile)
exportList.to_excel(writer, "Sheet1")
writer.save()

writer = ExcelWriter(allFile)
exportList.to_excel(writer, "Sheet1")
writer.save()
