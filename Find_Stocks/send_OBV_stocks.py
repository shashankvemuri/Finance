import yfinance as yf
import pandas as pd
import shutil
import os
import time
import glob
import smtplib
import ssl
from get_all_tickers import get_tickers as gt
from config import junk_email_password, junk_email_username, good_email_username
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from yahoo_fin import stock_info as si

'''
# tickers = gt.get_tickers_filtered(mktcap_min=150000, mktcap_max=10000000)
tickers = si.tickers_sp500()

print("The amount of stocks chosen to observe: " + str(len(tickers)))

shutil.rmtree("/Users/shashank/Documents/Code/Python/Outputs/daily_stock_report/stocks/")
os.mkdir("/Users/shashank/Documents/Code/Python/Outputs/daily_stock_report/stocks/")

Amount_of_API_Calls = 0
Stock_Failure = 0  
Stocks_Not_Imported = 0
i = 0

while (i < len(tickers)) and (Amount_of_API_Calls < 1800):
    try:
        stock = tickers[i] 
        temp = yf.Ticker(str(stock))
        Hist_data = temp.history(period="max") 
        Hist_data.to_csv("/Users/shashank/Documents/Code/Python/Outputs/daily_stock_report/stocks/"+stock+".csv") 
        time.sleep(2)  
        Amount_of_API_Calls += 1 
        Stock_Failure = 0
        i += 1 
    except ValueError:
        print("Yahoo Finance Backend Error, Attempting to Fix")
        if Stock_Failure > 5: 
            i+=1
            Stocks_Not_Imported += 1
        Amount_of_API_Calls += 1
        Stock_Failure += 1
print("The amount of stocks we successfully imported: " + str(i - Stocks_Not_Imported))
'''
list_files = (glob.glob("/Users/shashank/Documents/Code/Python/Outputs/daily_stock_report/stocks/*.csv")) 
new_data = []
interval = 0 

while interval < len(list_files):
    Data = pd.read_csv(list_files[interval]).tail(10)
    Data = Data.reset_index()
    Data = Data.drop(columns=['index'])

    pos_move = []
    neg_move = []
    OBV_Value = 0
    count = 0

    while (count < 10):
        try:
            if float(Data.iloc[count,1]) < float(Data.iloc[count,4]):
                pos_move.append(count)
            elif float(Data.iloc[count,1]) > float(Data.iloc[count,4]):
                neg_move.append(count)
            count += 1
        except:
            pass
    count2 = 0
    for i in pos_move:
        OBV_Value = round(OBV_Value + (Data.iloc[i,5]/Data.iloc[i,1]))
    for i in neg_move:
        OBV_Value = round(OBV_Value - (Data.iloc[i,5]/Data.iloc[i,1]))
    Stock_Name = ((os.path.basename(list_files[interval])).split(".csv")[0])
    new_data.append([Stock_Name, OBV_Value])
    interval += 1
df = pd.DataFrame(new_data, columns = ['Stock', 'OBV_Value'])
df["Stocks_Ranked"] = df["OBV_Value"].rank(ascending = False)
df.sort_values("OBV_Value", inplace = True, ascending = False)
df.to_csv("/Users/shashank/Documents/Code/Python/Outputs/Daily_Stock_Report/OBV_Ranked.csv", index = False)  # Save the dataframe to a csv without the index column

Analysis = pd.read_csv("/Users/shashank/Documents/Code/Python/Outputs/Daily_Stock_Report/OBV_Ranked.csv")  # Read in the ranked stocks
top10 = Analysis.head(10)
bottom10 = Analysis.tail(10)

html = """<html><head></head><body>Hello {}, <br/><br/> Here are the best On Balance Volume Stocks for today <br/> <br/> {} <br/> And here are the worst <br/> <br/> {} <br/>Best Regards,<br/>Your Computer</body></html>""".format('Shashank', top10.to_html(index=False), bottom10.to_html(index=False))
def send_email(email_recipient, email_subject):

    email_sender = junk_email_username()

    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = email_recipient
    msg['Subject'] = email_subject

    part1 = MIMEText(html, 'html')
    msg.attach(part1)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(email_sender, junk_email_password())
        text = msg.as_string()
        server.sendmail(email_sender, email_recipient, text)
        print('email sent')
        server.quit()
    except Exception as e:
        print (e)
    return True

send_email(good_email_username(), "Daily On Balance Volume Stock Report")