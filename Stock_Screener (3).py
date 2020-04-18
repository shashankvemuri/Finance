import urllib.request, urllib.error, urllib.parse
import time
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib
import pylab
import requests
from yahoo_fin import stock_info as si 
matplotlib.rcParams.update({'font.size': 9})

evenBetter = si.tickers_dow()


def rsiFunc(prices, n=14):
    deltas = np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed>=0].sum()/n
    down = -seed[seed<0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1.+rs)

    for i in range(n, len(prices)):
        delta = deltas[i-1] # the diff is 1 shorter

        if delta>0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up*(n-1) + upval)/n
        down = (down*(n-1) + downval)/n

        rs = up/down
        rsi[i] = 100. - 100./(1.+rs)

    return rsi

def movingaverage(values,window):
    weigths = np.repeat(1.0, window)/window
    smas = np.convolve(values, weigths, 'valid')
    return smas # as a numpy array

########EMA CALC ADDED############
def ExpMovingAverage(values, window):
    weights = np.exp(np.linspace(-1., 0., window))
    weights /= weights.sum()
    a =  np.convolve(values, weights, mode='full')[:len(values)]
    a[:window] = a[window]
    return a


def computeMACD(x, slow=26, fast=12):
    """
    compute the MACD (Moving Average Convergence/Divergence) using a fast and slow exponential moving avg'
    return value is emaslow, emafast, macd which are len(x) arrays
    """
    emaslow = ExpMovingAverage(x, slow)
    emafast = ExpMovingAverage(x, fast)
    return emaslow, emafast, emafast - emaslow

###############################
def graphData(stock,MA1,MA2):
    #######################################
    #######################################
    '''
        Use this to dynamically pull a stock:
    '''
    try:
        print('Currently Pulling',stock)


        netIncomeAr = []
        revAr = []
        ROCAr = []

        
        endLink = 'sort_order=asc&auth_token=a3fpXxHfsiN7AF4gjakQ'
        try:
            netIncome = urllib.request.urlopen('http://www.quandl.com/api/v1/datasets/OFDP/DMDRN_'+stock.upper()+'_NET_INC.csv?&'+endLink).read()
            revenue = urllib.request.urlopen('http://www.quandl.com/api/v1/datasets/OFDP/DMDRN_'+stock.upper()+'_REV_LAST.csv?&'+endLink).read()
            ROC = urllib.request.urlopen('http://www.quandl.com/api/v1/datasets/OFDP/DMDRN_'+stock.upper()+'_ROC.csv?&'+endLink).read()

            splitNI = netIncome.split('\n')
            print('Net Income:')
            for eachNI in splitNI[1:-1]:
                print(eachNI)
                netIncomeAr.append(eachNI)

            print('_________')
            splitRev = revenue.split('\n')
            print('Revenue:')
            for eachRev in splitRev[1:-1]:
                print(eachRev)
                revAr.append(eachRev)

            
            print('_________')
            splitROC = ROC.split('\n')
            print('Return on Capital:')
            for eachROC in splitROC[1:-1]:
                print(eachROC)
                ROCAr.append(eachROC)


            incomeDate, income = np.loadtxt(netIncomeAr, delimiter=',',unpack=True,
                                            converters={ 0: mdates.strpdate2num('%Y-%m-%d')})

            revDate, revenue = np.loadtxt(revAr, delimiter=',',unpack=True,
                                            converters={ 0: mdates.strpdate2num('%Y-%m-%d')})

            rocDate, ROC = np.loadtxt(ROCAr, delimiter=',',unpack=True,
                                            converters={ 0: mdates.strpdate2num('%Y-%m-%d')})

        except Exception as e:
            print('failed in the quandl grab')
            print(str(e))
            time.sleep(555)




        
        
        print(str(datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')))
        #Keep in mind this is close high low open, lol. 
        urlToVisit = 'http://chartapi.finance.yahoo.com/instrument/1.0/'+stock+'/chartdata;type=quote;range=10y/csv'
        stockFile =[]
        try:
            sourceCode = urllib.request.urlopen(urlToVisit).read()
            splitSource = sourceCode.split('\n')
            for eachLine in splitSource:
                splitLine = eachLine.split(',')
                if len(splitLine)==6:
                    if 'values' not in eachLine:
                        stockFile.append(eachLine)
        except Exception as e:
            print(str(e), 'failed to organize pulled data.')
    except Exception as e:
        print(str(e), 'failed to pull pricing data')
    #######################################
    #######################################
    try:   
        date, closep, highp, lowp, openp, volume = np.loadtxt(stockFile,delimiter=',', unpack=True,
                                                              converters={ 0: mdates.strpdate2num('%Y%m%d')})
        x = 0
        y = len(date)
        newAr = []
        while x < y:
            appendLine = date[x],openp[x],closep[x],highp[x],lowp[x],volume[x]
            newAr.append(appendLine)
            x+=1
            
        Av1 = movingaverage(closep, MA1)
        Av2 = movingaverage(closep, MA2)

        SP = len(date[MA2-1:])
            
        fig = plt.figure(facecolor='#07000d')

        ax1 = plt.subplot2grid((9,4), (1,0), rowspan=4, colspan=4, axisbg='#07000d')
        candlestick_ohlc(ax1, newAr[-SP:], width=.6, colorup='#53c156', colordown='#ff1717')

        Label1 = str(MA1)+' SMA'
        Label2 = str(MA2)+' SMA'

        ax1.plot(date[-SP:],Av1[-SP:],'#e1edf9',label=Label1, linewidth=1.5)
        ax1.plot(date[-SP:],Av2[-SP:],'#4ee6fd',label=Label2, linewidth=1.5)
        
        ax1.grid(True, color='w')
        ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax1.yaxis.label.set_color("w")
        ax1.spines['bottom'].set_color("#5998ff")
        ax1.spines['top'].set_color("#5998ff")
        ax1.spines['left'].set_color("#5998ff")
        ax1.spines['right'].set_color("#5998ff")
        ax1.tick_params(axis='y', colors='w')
        plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
        ax1.tick_params(axis='x', colors='w')
        plt.ylabel('Stock price and Volume')

        maLeg = plt.legend(loc=9, ncol=2, prop={'size':7},
                   fancybox=True, borderaxespad=0.)
        maLeg.get_frame().set_alpha(0.4)
        textEd = pylab.gca().get_legend().get_texts()
        pylab.setp(textEd[0:5], color = 'w')

        volumeMin = 0
        
        ax0 = plt.subplot2grid((9,4), (0,0), sharex=ax1, rowspan=1, colspan=4, axisbg='#07000d')
        rsi = rsiFunc(closep)
        rsiCol = '#c1f9f7'
        posCol = '#386d13'
        negCol = '#8f2020'
        
        ax0.plot(date[-SP:], rsi[-SP:], rsiCol, linewidth=1.5)
        ax0.axhline(70, color=negCol)
        ax0.axhline(30, color=posCol)
        ax0.fill_between(date[-SP:], rsi[-SP:], 70, where=(rsi[-SP:]>=70), facecolor=negCol, edgecolor=negCol, alpha=0.5)
        ax0.fill_between(date[-SP:], rsi[-SP:], 30, where=(rsi[-SP:]<=30), facecolor=posCol, edgecolor=posCol, alpha=0.5)
        ax0.set_yticks([30,70])
        ax0.yaxis.label.set_color("w")
        ax0.spines['bottom'].set_color("#5998ff")
        ax0.spines['top'].set_color("#5998ff")
        ax0.spines['left'].set_color("#5998ff")
        ax0.spines['right'].set_color("#5998ff")
        ax0.tick_params(axis='y', colors='w')
        ax0.tick_params(axis='x', colors='w')
        plt.ylabel('RSI')

        ax1v = ax1.twinx()
        ax1v.fill_between(date[-SP:],volumeMin, volume[-SP:], facecolor='#00ffe8', alpha=.4)
        ax1v.axes.yaxis.set_ticklabels([])
        ax1v.grid(False)
        ###Edit this to 3, so it's a bit larger
        ax1v.set_ylim(0, 3*volume.max())
        ax1v.spines['bottom'].set_color("#5998ff")
        ax1v.spines['top'].set_color("#5998ff")
        ax1v.spines['left'].set_color("#5998ff")
        ax1v.spines['right'].set_color("#5998ff")
        ax1v.tick_params(axis='x', colors='w')
        ax1v.tick_params(axis='y', colors='w')
        ax2 = plt.subplot2grid((9,4), (5,0), sharex=ax1, rowspan=1, colspan=4, axisbg='#07000d')
        fillcolor = '#00ffe8'
        nslow = 26
        nfast = 12
        nema = 9
        emaslow, emafast, macd = computeMACD(closep)
        ema9 = ExpMovingAverage(macd, nema)
        ax2.plot(date[-SP:], macd[-SP:], color='#4ee6fd', lw=2)
        ax2.plot(date[-SP:], ema9[-SP:], color='#e1edf9', lw=1)
        ax2.fill_between(date[-SP:], macd[-SP:]-ema9[-SP:], 0, alpha=0.5, facecolor=fillcolor, edgecolor=fillcolor)

        plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
        ax2.spines['bottom'].set_color("#5998ff")
        ax2.spines['top'].set_color("#5998ff")
        ax2.spines['left'].set_color("#5998ff")
        ax2.spines['right'].set_color("#5998ff")
        ax2.tick_params(axis='x', colors='w')
        ax2.tick_params(axis='y', colors='w')
        plt.ylabel('MACD', color='w')
        ax2.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='upper'))

        ######################################
        ######################################
        ax3 = plt.subplot2grid((9,4), (6,0), sharex=ax1, rowspan=1, colspan=4, axisbg='#07000d')
        ax3.plot(incomeDate,income,'#4ee6fd')
        ax3.spines['bottom'].set_color("#5998ff")
        ax3.spines['top'].set_color("#5998ff")
        ax3.spines['left'].set_color("#5998ff")
        ax3.spines['right'].set_color("#5998ff")
        ax3.tick_params(axis='x', colors='w')
        ax3.tick_params(axis='y', colors='w')
        ax3.yaxis.set_major_locator(mticker.MaxNLocator(nbins=4, prune='upper'))
        plt.ylabel('NI', color='w')

        ax4 = plt.subplot2grid((9,4), (7,0),sharex=ax1, rowspan=1, colspan=4, axisbg='#07000d')
        ax4.plot(revDate, revenue,'#4ee6fd')
        ax4.spines['bottom'].set_color("#5998ff")
        ax4.spines['top'].set_color("#5998ff")
        ax4.spines['left'].set_color("#5998ff")
        ax4.spines['right'].set_color("#5998ff")
        ax4.tick_params(axis='x', colors='w')
        ax4.tick_params(axis='y', colors='w')
        ax4.yaxis.set_major_locator(mticker.MaxNLocator(nbins=4, prune='upper'))
        plt.ylabel('Rev', color='w')

        ax5 = plt.subplot2grid((9,4), (8,0), rowspan=1, sharex=ax1, colspan=4, axisbg='#07000d')
        ax5.plot(rocDate, ROC,'#4ee6fd')
        ax5.spines['bottom'].set_color("#5998ff")
        ax5.spines['top'].set_color("#5998ff")
        ax5.spines['left'].set_color("#5998ff")
        ax5.spines['right'].set_color("#5998ff")
        ax5.tick_params(axis='x', colors='w')
        ax5.tick_params(axis='y', colors='w')
        ax5.yaxis.set_major_locator(mticker.MaxNLocator(nbins=4, prune='upper'))
        plt.ylabel('ROC', color='w')



        
        for label in ax5.xaxis.get_ticklabels():
            label.set_rotation(45)

        plt.suptitle(stock,color='w')

        plt.setp(ax0.get_xticklabels(), visible=False)
        ### add this ####
        plt.setp(ax1.get_xticklabels(), visible=False)
        plt.setp(ax2.get_xticklabels(), visible=False)
        plt.setp(ax3.get_xticklabels(), visible=False)
        plt.setp(ax4.get_xticklabels(), visible=False)
        
        

        plt.subplots_adjust(left=.09, bottom=.14, right=.94, top=.95, wspace=.20, hspace=0)
        plt.show()
        fig.savefig('example.png',facecolor=fig.get_facecolor())
           
    except Exception as e:
        print('main loop',str(e))



def screener(stock):
    try:
        #print 'doing',stock
        sourceCode = urllib.request.urlopen('http://finance.yahoo.com/q/ks?s='+stock).read()
        pbr = sourceCode.split('Price/Book (mrq):</td><td class="yfnc_tabledata1">')[1].split('</td>')[0]
        #print 'price to book ratio:',stock,pbr

        if float(pbr) < 1:
            #print 'price to book ratio:',stock,pbr

            PEG5 = sourceCode.split('PEG Ratio (5 yr expected)<font size="-1"><sup>1</sup></font>:</td><td class="yfnc_tabledata1">')[1].split('</td>')[0]
            if 0 < float(PEG5) < 2:
                #print 'PEG forward 5 years',PEG5
                
                
                DE = sourceCode.split('Total Debt/Equity (mrq):</td><td class="yfnc_tabledata1">')[1].split('</td>')[0]
                #print 'Debt to Equity:',DE
                #if 0 < float(DE) < 2:
                PE12 = sourceCode.split('Trailing P/E (ttm, intraday):</td><td class="yfnc_tabledata1">')[1].split('</td>')[0]
                #print 'Trailing PE (12mo):',PE12
                if float(PE12) < 15:
                    # Your own SCREENED array.... 
                    #evenBetter.append(stock)
                    
                    print('______________________________________')
                    print('')
                    print(stock,'meets requirements')
                    print('price to book:',pbr)
                    print('PEG forward 5 years',PEG5)
                    print('Trailing PE (12mo):',PE12)
                    print('Debt to Equity:',DE)
                    print('______________________________________')

                    if showCharts.lower() == 'y':

                        try:
                            graphData(stock,25,50)

                        except Exception as e:
                            print('failed the main quandl loop for reason of',str(e))

            
    except Exception as e:
        #print 'failed in the main loop',str(e)
        pass

showCharts = input('Would you like to show the financial data (Quandl) charts? (Y/N): ')

if showCharts.lower()=='y':
    print('okay, charts will be shown')

elif showCharts.lwoer()=='n':
    print('okay, charts will NOT be shown.')

else:
    print('invalid input, charts will NOT be shown.')

        

for eachStock in evenBetter:
    screener(eachStock)
    