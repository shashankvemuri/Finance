from lxml import html  
import requests
from time import sleep
import json
import argparse
from collections import OrderedDict
from time import sleep

def matching(string, begTok, endTok):
    # Find location of the beginning token
    start = string.find(begTok)
    stack = []
    # Append it to the stack
    stack.append(start)
    # Loop through rest of the string until we find the matching ending token
    for i in range(start+1, len(string)):
        if begTok in string[i]:
            stack.append(i)
        elif endTok in string[i]:
            stack.remove(stack[len(stack)-1])
        if len(stack) == 0:
            # Removed the last begTok so we're done
            end = i+1
            break
    return end

def parse(ticker):
    # Yahoo Finance summary for stock, mutual fund or ETF
    url = "http://finance.yahoo.com/quote/%s?p=%s"%(ticker,ticker)
    response = requests.get(url, verify=False)
    print ("Parsing %s"%(url))
    sleep(4)
    summary_data = OrderedDict()

    # Convert the _context html object into JSON blob to tell if this is an equity, a mutual fund or an ETF
    contextStart = response.text.find('"_context"')
    contextEnd = contextStart+matching(response.text[contextStart:len(response.text)], '{', '}')
    
    # Convert the QuoteSummaryStore html object into JSON blob
    summaryStart = response.text.find('"QuoteSummaryStore"')
    summaryEnd = summaryStart+matching(response.text[summaryStart:len(response.text)], '{', '}')
    
    # Convert the ticker quote html object into JSON blob
    streamStart = response.text.find('"StreamDataStore"')
    quoteStart = streamStart+response.text[streamStart:len(response.text)].find("%s"%ticker.upper())-1
    quoteEnd = quoteStart+matching(response.text[quoteStart:len(response.text)], '{', '}')
    
    try:
        json_loaded_context = json.loads('{' + response.text[contextStart:contextEnd] + '}')
        json_loaded_summary = json.loads('{' + response.text[summaryStart:summaryEnd] + '}')
        # Didn't end up needing this for the summary details, but there's lots of good data there
        #json_loaded_quote = json.loads('{' + response.text[quoteStart:quoteEnd] + '}')
        if "EQUITY" in json_loaded_context["_context"]["quoteType"]:
            # Define all the data that appears on the Yahoo Financial summary page for a stock
            # Use http://beautifytools.com/html-beautifier.php to understand where the path came from or to add any additional data
            prev_close = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["previousClose"]['fmt']
            mark_open = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["open"]['fmt']
            bid = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["bid"]['fmt'] + " x "\
            + str(json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["bidSize"]['raw'])
            ask = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["ask"]['fmt'] + " x "\
            + str(json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["askSize"]['raw'])
            day_range = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["regularMarketDayLow"]['fmt']\
            + " - " + json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["regularMarketDayHigh"]['fmt']
            year_range = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["fiftyTwoWeekLow"]['fmt'] + " - "\
            + json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["fiftyTwoWeekHigh"]['fmt']
            volume = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["volume"]['longFmt']
            avg_volume = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["averageVolume"]['longFmt']
            market_cap = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["marketCap"]['fmt']
            beta = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["beta"]['fmt']
            PE = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["trailingPE"]['fmt']
            eps = json_loaded_summary["QuoteSummaryStore"]["defaultKeyStatistics"]["trailingEps"]['fmt']
            earnings_list = json_loaded_summary["QuoteSummaryStore"]["calendarEvents"]['earnings']
            datelist = []
            for i in earnings_list['earningsDate']:
                datelist.append(i['fmt'])
            earnings_date = ' to '.join(datelist)
            div = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["dividendRate"]['fmt'] + " ("\
            + json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["dividendYield"]['fmt'] + ")"
            ex_div_date = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["exDividendDate"]['fmt']
            y_Target_Est = json_loaded_summary["QuoteSummaryStore"]["financialData"]["targetMeanPrice"]['raw']
            
            # Store ordered pairs to be written to a file
            summary_data.update({'Previous Close':prev_close,'Open':mark_open,'Bid':bid,'Ask':ask,"Day's Range":day_range\
            ,'52 Week Range':year_range,'Volume':volume,'Avg. Volume':avg_volume,'Market Cap':market_cap,'Beta (3Y Monthly)':beta\
            ,'PE Ratio (TTM)':PE,'EPS (TTM)':eps,'Earnings Date':earnings_date,'Forward Dividend & Yield':div\
            ,'Ex-Dividend Date':ex_div_date,'1y Target Est':y_Target_Est,'ticker':ticker,'url':url})
            return summary_data
        elif "MUTUALFUND" in json_loaded_context["_context"]["quoteType"]:
            # Define all the data that appears on the Yahoo Financial summary page for a mutual fund
            prev_close = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["previousClose"]['fmt']
            ytd_return = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["ytdReturn"]['fmt']
            exp_rat = json_loaded_summary["QuoteSummaryStore"]["defaultKeyStatistics"]["annualReportExpenseRatio"]['fmt']
            category = json_loaded_summary["QuoteSummaryStore"]["fundProfile"]["categoryName"]
            last_cap_gain = json_loaded_summary["QuoteSummaryStore"]["defaultKeyStatistics"]["lastCapGain"]['fmt']
            morningstar_rating = json_loaded_summary["QuoteSummaryStore"]["defaultKeyStatistics"]["morningStarOverallRating"]['raw']
            morningstar_risk_rating = json_loaded_summary["QuoteSummaryStore"]["defaultKeyStatistics"]["morningStarRiskRating"]['raw']
            sustainability_rating = json_loaded_summary["QuoteSummaryStore"]["esgScores"]["sustainScore"]['raw']
            net_assets = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["totalAssets"]['fmt']
            beta = json_loaded_summary["QuoteSummaryStore"]["defaultKeyStatistics"]["beta3Year"]['fmt']
            yld = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["yield"]['fmt']
            five_year_avg_ret = json_loaded_summary["QuoteSummaryStore"]["fundPerformance"]["performanceOverview"]["fiveYrAvgReturnPct"]['fmt']
            holdings_turnover = json_loaded_summary["QuoteSummaryStore"]["defaultKeyStatistics"]["annualHoldingsTurnover"]['fmt']
            div = json_loaded_summary["QuoteSummaryStore"]["defaultKeyStatistics"]["lastDividendValue"]['fmt']
            inception_date = json_loaded_summary["QuoteSummaryStore"]["defaultKeyStatistics"]["fundInceptionDate"]['fmt']
        
            # Store ordered pairs to be written to a file
            summary_data.update({'Previous Close':prev_close,'YTD Return':ytd_return,'Expense Ratio (net)':exp_rat,'Category':category\
            ,'Last Cap Gain':last_cap_gain,'Morningstar Rating':morningstar_rating,'Morningstar Risk Rating':morningstar_risk_rating\
            ,'Sustainability Rating':sustainability_rating,'Net Assets':net_assets,'Beta (3Y Monthly)':beta,'Yield':yld\
            ,'5y Average Return':five_year_avg_ret,'Holdings Turnover':holdings_turnover,'Last Dividend':div,'Average for Category':'N/A'\
            ,'Inception Date':inception_date,'ticker':ticker,'url':url})
            return summary_data
        elif "ETF" in json_loaded_context["_context"]["quoteType"]:
            # Define all the data that appears on the Yahoo Financial summary page for an ETF
            prev_close = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["previousClose"]['fmt']
            mark_open = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["open"]['fmt']
            bid = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["bid"]['fmt'] + " x "\
            + str(json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["bidSize"]['raw'])
            ask = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["ask"]['fmt'] + " x "\
            + str(json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["askSize"]['raw'])
            day_range = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["regularMarketDayLow"]['fmt'] + " - "\
            + json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["regularMarketDayHigh"]['fmt']
            year_range = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["fiftyTwoWeekLow"]['fmt'] + " - "\
            + json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["fiftyTwoWeekHigh"]['fmt']
            volume = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["volume"]['longFmt']
            avg_volume = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["averageVolume"]['longFmt']
            net_assets = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["totalAssets"]['fmt']
            nav = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["navPrice"]['fmt']
            yld = json_loaded_summary["QuoteSummaryStore"]["summaryDetail"]["yield"]['fmt']
            ytd_return = json_loaded_summary["QuoteSummaryStore"]["defaultKeyStatistics"]["ytdReturn"]['fmt']
            beta = json_loaded_summary["QuoteSummaryStore"]["defaultKeyStatistics"]['beta3Year']['fmt']
            exp_rat = json_loaded_summary["QuoteSummaryStore"]["fundProfile"]["feesExpensesInvestment"]["annualReportExpenseRatio"]['fmt']
            inception_date = json_loaded_summary["QuoteSummaryStore"]["defaultKeyStatistics"]["fundInceptionDate"]['fmt']
        
            # Store ordered pairs to be written to a file
            summary_data.update({'Previous Close':prev_close,'Open':mark_open,'Bid':bid,'Ask':ask,"Day's Range":day_range,'52 Week Range':year_range\
            ,'Volume':volume,'Avg. Volume':avg_volume,'Net Assets':net_assets,'NAV':nav,'PE Ratio (TTM)':'N/A','Yield':yld,'YTD Return':ytd_return\
            ,'Beta (3Y Monthly)':beta,'Expense Ratio (net)':exp_rat,'Inception Date':inception_date,'ticker':ticker,'url':url})
            return summary_data
    except:
        print ("Failed to parse json response")
        return {"error":"Failed to parse json response"}
        
if __name__=="__main__":
    ticker = input("Enter a ticker: ")
    print ("Fetching data for %s"%(ticker))
    scraped_data = parse(ticker)
    print ("Writing data to output file")
    with open('%s-summary.json'%(ticker),'w') as fp:
        json.dump(scraped_data,fp,indent = 4)