import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf
from pandas_datareader import data as pdr
import xlsxwriter
import requests
from yahoo_fin import stock_info as si
import pickle
import bs4 as bs

# You need to change this to a convenient spot on your own hard drive.

my_path = '/Users/shashank/Downloads/Code/Finance'
threshold = 0.80

# You need to go to Yahoo and download a list of the S&P 500 components. Make sure to save it to
# a CSV file with column headers that include "Symbol", "Date" and "Close" 
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
        
sp500_tickers = save_spx_tickers()

# Make the ticker symbols readable by Yahoo Finance
sp500_tickers = [item.replace(".", "-") for item in sp500_tickers]

# Upload a list of the S&P 500 components downloaded from Yahoo.
mylist= []
mylist2 = []

df_sp500_tickers = pd.DataFrame(list(zip(sp500_tickers)), columns =['Symbol'])

# This module loops through the S&P 500 tickers, downloads the data from Yahoo and creates a separate CSV 
# file of historical data for each ticker (e.g. AAPL.csv).
# Skip this routine if you already have the CSV files available.
'''
for index, ticker in df_sp500_tickers.iterrows():
    global df
    
    my_ticker = ticker['Symbol']
    
    yf_ticker = yf.Ticker(my_ticker)
    data = yf_ticker.history(period="max")
    df = pd.DataFrame(data)
    df.reset_index(level=0, inplace=True)
    df['Symbol'] = my_ticker
    df = df[['Symbol','Date','Close']]
    df.drop_duplicates(subset ="Date", keep = 'first', inplace = True) #Yahoo has a tendency to duplicate the last row.
    df.to_csv(path_or_buf = my_path + "/data/" + my_ticker +".csv", index=False)
'''
# Creates the dataframe container for the stats data.
df_tradelist = pd.DataFrame(index=[], columns=['my_ticker', 'hold_per', 'pct_uprows', 'max_up_return', 'min_up_return', 'avg_up_return', 'avg_down_return', 'exp_return', 'stdev_returns', 'pct_downside', 'worst_return', 'least_pain_pt', 'total_years', 'max_consec_beat', 'best_buy_date', 'best_sell_date', 'analyzed_years'])
df_tradelist.head()

# Convert prices to holding period returns based on 20 trading days per month.
def convert_prices_to_periods():
    
    global dperiods
    global dfr
        
    dfr = df.pct_change(periods = dperiods)
    dfr.reset_index(level=0, inplace=True)
    dfr.rename(columns={'Close':'Returns'}, inplace=True)
    dfr = dfr.round(4)

# Separate out the date column into separate month, year and day values.
def separate_date_column():
    
    global dfr
    
    dfr['Month'] = pd.DatetimeIndex(dfr['Date']).month
    dfr['Day'] = pd.DatetimeIndex(dfr['Date']).day
    dfr['Year'] = pd.DatetimeIndex(dfr['Date']).year
    dfr['M-D'] = dfr['Month'].astype(str)+'-'+dfr['Day'].astype(str)
    pd.set_option('display.max_rows', len(dfr))

# Pivot the table to show years across the top and Month-Day values in the first column on the left.
def pivot_the_table():
    
    global dfr_pivot
    
    dfr_pivot = dfr.pivot(index='M-D', columns='Year', values='Returns')
    dfr_pivot.reset_index(level=0, inplace=True)
    dfr_pivot = pd.DataFrame(dfr_pivot)
    dfr_pivot.columns.name="Index"

    # The pivot operation created empty cells for weekends and holiday, so I filled them with EOD values from
    # the previous trading day.
    dfr_pivot.fillna(method='ffill', inplace=True)
    
    # As of this date, 1/22/2020, we are only evaluating results through 12/31/2019, so we will drop the
    # 2020 year column.
    if 2020 in dfr_pivot.columns:
        dfr_pivot.drop(2020, axis=1, inplace=True)
    

# Add additional calculated columns to facilitate statistic calculations for each stock.
def add_calculated_items():
    
    global dfr_pivot
    global lookback
    global start
    
    # The lookback figure is the number (must be an integer) of years back from last year (2019) that you want to include in
    # analysis, i.e. the calculations below. It's probably a good idea to keep it at 20 years or less
    # to reflect more recent market conditions.
    lookback = 20
    start = 1
    
    if lookback > len(dfr_pivot.columns) - 1:
        start = 1
    else:
        start = len(dfr_pivot.columns) - lookback
    
    dfr_pivot['YearCount'] = dfr_pivot.count(axis=1, numeric_only=True)
    dfr_pivot['Lookback'] = lookback
    dfr_pivot['UpCount'] = dfr_pivot[dfr_pivot.iloc[:,start:len(dfr_pivot.columns)-2] > 0].count(axis=1)
    dfr_pivot['DownCount'] = dfr_pivot[dfr_pivot.iloc[:,start:len(dfr_pivot.columns)] < 0].count(axis=1)
    dfr_pivot['PctUp'] = dfr_pivot['UpCount']/dfr_pivot['Lookback']
    dfr_pivot['PctDown'] = dfr_pivot['DownCount']/dfr_pivot['Lookback']
    dfr_pivot['AvgReturn'] = dfr_pivot.iloc[:,start:len(dfr_pivot.columns)-6].mean(axis=1)
    dfr_pivot['StDevReturns'] = dfr_pivot.iloc[:,start:len(dfr_pivot.columns)-7].std(axis=1)
    dfr_pivot['67PctDownside'] = dfr_pivot['AvgReturn']-dfr_pivot['StDevReturns']
    dfr_pivot['MaxReturn'] = dfr_pivot.iloc[:,start:len(dfr_pivot.columns)-9].max(axis=1)
    dfr_pivot['MinReturn'] = dfr_pivot.iloc[:,start:len(dfr_pivot.columns)-10].min(axis=1)

# Add a fictional date column in Python date/time format so the table can be sorted by date. Then sort by Date.
# Reset the index and round the float values to 4 decimals.
def sortbydate_resetindex_export():
    
    global dfr_pivot
    
    dfr_pivot['Date'] = '2000-' + dfr_pivot['M-D'].astype(str)
    dfr_pivot['Date'] = pd.to_datetime(dfr_pivot['Date'], infer_datetime_format=True)
    dfr_pivot.sort_values(by='Date',ascending=True, inplace=True)
        
    dfr_pivot.reset_index(inplace=True)
    dfr_pivot = dfr_pivot.round(4)

# Calculate the trading statistics for the rolling holding periods for the stock.
def calc_trading_stats():
    
    global interval
    global dfr_pivot
    global pct_uprows
    global max_up_return
    global min_up_return
    global avg_up_return
    global avg_down_return
    global exp_return
    global stdev_returns
    global pct_downside
    global worst_return
    global least_pain_pt
    global total_years
    global n_consec
    global max_n_consec
    global max_consec_beat
    global best_sell_date
    global best_buy_date
    global analyzed_years
    global lookback
    
    pct_uprows = (dfr_pivot.loc[dfr_pivot['PctUp'] > threshold, 'PctUp'].count() / dfr_pivot.loc[:, 'PctUp'].count()).astype(float).round(4)
    max_up_return = dfr_pivot.loc[dfr_pivot['PctUp'] > threshold, 'MaxReturn'].max()
    min_up_return = dfr_pivot.loc[dfr_pivot['PctUp'] > threshold, 'MinReturn'].min()
    avg_up_return = dfr_pivot.loc[dfr_pivot['PctUp'] > 0.5, 'AvgReturn'].mean()
    avg_up_return = np.float64(avg_up_return).round(4)
    avg_down_return = dfr_pivot.loc[dfr_pivot['PctDown'] > 0.5, 'AvgReturn'].mean()
    avg_down_return = np.float64(avg_down_return).round(4)
    exp_return = round(dfr_pivot['AvgReturn'].mean(), 4)
    stdev_returns = dfr_pivot['StDevReturns'].mean()
    stdev_returns = np.float64(stdev_returns).round(4)
    worst_return = dfr_pivot['MinReturn'].min()
    pct_downside = exp_return - stdev_returns
    pct_downside = np.float64(pct_downside).round(4)
    least_pain_pt = dfr_pivot.loc[dfr_pivot['PctUp'] > threshold, '67PctDownside'].max()
    total_years = dfr_pivot['YearCount'].max()
    analyzed_years = lookback
    
    n_consec = 0
    max_n_consec = 0

    for x in dfr_pivot['PctUp']:
        if (x > threshold):
            n_consec += 1
        else: # check for new max, then start again from 1
            max_n_consec = max(n_consec, max_n_consec)
            n_consec = 1

    max_consec_beat = max_n_consec

    try:
        best_sell_date = dfr_pivot.loc[dfr_pivot['67PctDownside'] == least_pain_pt, 'M-D'].iloc[0]
    except:
        best_sell_date = "nan"

    try:
        row = dfr_pivot.loc[dfr_pivot['M-D'] == best_sell_date, 'M-D'].index[0] - interval
        col = dfr_pivot.columns.get_loc('M-D')
        best_buy_date = dfr_pivot.iloc[row,col]
    except:
        best_buy_date = "nan"


# If the pct_uprows and history conditions are met, then create the array of stat values and append 
# it to the recommended trade list.
def filter_and_append_stats():
    
    global statsdata
    global df_statsdata
    global df_tradelist
    
    # Save the stats data separately to export to Excel for further research on each ticker if desired.
    statsdata = np.array([my_ticker, hold_per, pct_uprows, max_up_return, min_up_return, avg_up_return, avg_down_return, exp_return, stdev_returns, pct_downside, worst_return, least_pain_pt, total_years, max_consec_beat, best_buy_date, best_sell_date, analyzed_years])
    df_statsdata = pd.DataFrame(statsdata.reshape(-1, len(statsdata)), columns=['my_ticker', 'hold_per', 'pct_uprows', 'max_up_return', 'min_up_return', 'avg_up_return', 'avg_down_return', 'exp_return', 'stdev_returns', 'pct_downside', 'worst_return', 'least_pain_pt', 'total_years', 'max_consec_beat', 'best_buy_date', 'best_sell_date', 'analyzed_years'])
    
    if pct_uprows > 0.1:
        if total_years > 9:
            df_tradelist = df_tradelist.append(dict(zip(df_tradelist.columns, statsdata)), ignore_index=True)
            
# This module grabs each ticker file, transforms it and calculates the statistics needed for a 90 day holding period.
def calc_3month_returns():
    
    global dfr
    global dfr_pivot
    global df_tradelist
    global dfr_3mo
    global df_statsdata_3mo
    global threshold
    global hold_per
    global dperiods
    global interval
    
    dperiods = 60
    hold_per = "3 Mos"
    interval = 90
    
    convert_prices_to_periods()
    
    separate_date_column()

    pivot_the_table()

    add_calculated_items()

    sortbydate_resetindex_export()
    
    # Export the pivot table to CSV for further research if desired.
    #dfr_pivot.to_csv(path_or_buf = my_path + "/data/" + my_ticker + "_dfr_pivot_3mo.csv", index=False)
    
    # Save dfr_pivot to separate dataframe for exporting to Excel
    dfr_3mo = pd.DataFrame(dfr_pivot)

    calc_trading_stats()
    
    filter_and_append_stats()
    
    # Save statsdata to separate dataframe for exporting to Excel
    df_statsdata_3mo = df_statsdata.copy()
    
# This module grabs each ticker file, transforms it and calculates the statistics needed for a 60 day holding period.
def calc_2month_returns():
    
    global dfr
    global dfr_pivot
    global df_tradelist
    global dfr_2mo
    global df_statsdata_2mo
    global threshold
    global hold_per
    global dperiods
    global interval
    
    dperiods = 40
    hold_per = "2 Mos"
    interval = 60

    convert_prices_to_periods()
    
    separate_date_column()

    pivot_the_table()

    add_calculated_items()

    sortbydate_resetindex_export()
    
    # Export the pivot table to CSV for further research if desired.
    #dfr_pivot.to_csv(path_or_buf = my_path + "/data/" + my_ticker + "_dfr_pivot_2mo.csv", index=False)
    
    # Save dfr_pivot to separate dataframe for exporting to Excel
    dfr_2mo = pd.DataFrame(dfr_pivot)

    calc_trading_stats()
        
    filter_and_append_stats()
     
    # Save statsdata to separate dataframe for exporting to Excel
    df_statsdata_2mo = df_statsdata.copy()
            

# This module grabs each ticker file, transforms it and calculates the statistics needed for a 30 day holding period.
def calc_1month_returns():
    
    global dfr
    global dfr_pivot
    global df_tradelist
    global dfr_1mo
    global df_statsdata_1mo
    global threshold
    global hold_per
    global dperiods
    global interval
    
    dperiods = 20
    hold_per = "1 Mo"
    interval = 30

    convert_prices_to_periods()
    
    separate_date_column()

    pivot_the_table()

    add_calculated_items()

    sortbydate_resetindex_export()
    
    # Export the pivot table to CSV for further research if desired.
    #dfr_pivot.to_csv(path_or_buf = my_path + "/data/" + my_ticker + "_dfr_pivot_1mo.csv", index=False)
    
    # Save dfr_pivot to separate dataframe for exporting to Excel
    dfr_1mo = pd.DataFrame(dfr_pivot)

    calc_trading_stats()
        
    filter_and_append_stats()
    
    # Save statsdata to separate dataframe for exporting to Excel
    df_statsdata_1mo = df_statsdata.copy()
            

# Build and export an Excel file for each ticker using XlsxWriter
def export_to_excel():
    
    excel_file_path = my_path + "/data/" + my_ticker + ".xlsx"
    
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(excel_file_path, engine='xlsxwriter')

    # Convert the dataframe to an XlsxWriter Excel object.
    df_statsdata_1mo.to_excel(writer, sheet_name='Stats', index=False)
    df_statsdata_2mo.to_excel(writer, sheet_name='Stats', startrow=2, header=False, index=False)
    df_statsdata_3mo.to_excel(writer, sheet_name='Stats', startrow=3, header=False, index=False)
    dfr_1mo.to_excel(writer, sheet_name='1 Mo Returns', index=False)
    dfr_2mo.to_excel(writer, sheet_name='2 Mo Returns', index=False)
    dfr_3mo.to_excel(writer, sheet_name='3 Mo Returns', index=False)

    # Get the xlsxwriter objects from the dataframe writer object.
    workbook  = writer.book
    worksheet1 = writer.sheets['Stats']
    worksheet2 = writer.sheets['1 Mo Returns']
    worksheet3 = writer.sheets['2 Mo Returns']
    worksheet4 = writer.sheets['3 Mo Returns']
    
    # Add conditional formatting to highlight positive returns in green
    end_column = dfr_1mo.columns.get_loc("YearCount")
    grn_format = workbook.add_format({'bg_color':   '#C6EFCE','font_color': '#006100'})
    worksheet2.conditional_format(1, 2, 365, end_column - 1,{'type':'cell','criteria':'>','value':0,'format':grn_format})
    worksheet3.conditional_format(1, 2, 365, end_column - 1,{'type':'cell','criteria':'>','value':0,'format':grn_format})
    worksheet4.conditional_format(1, 2, 365, end_column - 1,{'type':'cell','criteria':'>','value':0,'format':grn_format})
    
    # Freeze panes for scrolling
    worksheet2.freeze_panes(1, 2)
    worksheet3.freeze_panes(1, 2)
    worksheet4.freeze_panes(1, 2)
    
    # Save the file
    writer.save()

# Read CSV files by ticker, transform and extract stats from each one.
for index, ticker in df_sp500_tickers.iterrows():
    global dfr
    
    my_ticker = ticker['Symbol']

    df = pd.read_csv (my_path + "/data/" + my_ticker + ".csv")
    df.set_index('Date', inplace=True)
    df = df['Close']
    df = pd.DataFrame(df, columns=['Close'])
    
    calc_1month_returns()
    
    calc_2month_returns()
    
    calc_3month_returns()
    
    export_to_excel()

# Make a copy and convert the trade list to a Pandas dataframe.
df_tradelist_copy = df_tradelist.copy()
df_tradelist = pd.DataFrame(df_tradelist)


#df_tradelist.to_csv(path_or_buf = my_path + "/df_tradelist.csv", index=False)
#df_tradelist_copy.to_csv(path_or_buf = my_path + "/df_tradelist_copy.csv", index=False)


# Clean it up by removing rows with NaN's and infinity values and dropping duplicates.
df_tradelist.replace("inf", np.nan, inplace=True)
df_tradelist.dropna(inplace=True)
df_tradelist = df_tradelist[~df_tradelist.max_up_return.str.contains("nan")]
df_tradelist = df_tradelist[~df_tradelist.avg_down_return.str.contains("nan")]
df_tradelist.sort_values(by=['pct_uprows'], ascending=False)
df_tradelist.drop_duplicates(subset ="my_ticker", keep = 'first', inplace = True) 

df_tradelist.tail(10)

df_tradelist.head()
#df_tradelist.shape

# Export the trade list to CSV files for execution and/or further research if desired.
df_tradelist.to_csv(path_or_buf = my_path + "/df_tradelist.csv", index=False)