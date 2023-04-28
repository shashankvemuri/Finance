import os
import smtplib
import imghdr
from email.message import EmailMessage
import yfinance as yf
import datetime as dt
import pandas as pd
from pandas_datareader import data as pdr
import time

# Get email address and password from environment variables
EMAIL_ADDRESS = os.environ.get('EMAIL_USER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASS')

# Initialize email message object
msg = EmailMessage()

# Set the start date and current date
start = dt.datetime(2018,12,1)
now = dt.datetime.now()

# Set the stock and the target price
stock="QQQ"
TargetPrice = 180

# Set the subject, from, and to fields of the email message
msg['Subject'] = 'Alert on '+ stock+'!'
msg['From'] = ''
msg['To'] = ''

# Initialize the alerted flag
alerted=False

# Loop to check for the condition and send the email
while 1:
    # Get the stock data from Yahoo Finance API
    df = pdr.get_data_yahoo(stock, start, now)
    currentClose=df["Adj Close"][-1]

    # Check if the current close price is greater than the target price and if alerted flag is False
    condition=currentClose>TargetPrice
    if(condition and alerted==False):
        # Set the alerted flag to True and create the message
        alerted=True
        message=stock +" Has activated the alert price of "+ str(TargetPrice) +\
            "\nCurrent Price: "+ str(currentClose)
        print(message)
        # Set the content of the email message
        msg.set_content(message)

        # Attach any files to the email message
        files=[r""]

        for file in files:
            with open(file,'rb') as f:
                file_data=f.read()
                file_name=""

                msg.add_attachment(file_data, maintype="application",
                    subtype='ocetet-stream', filename=file_name)

        # Send the email message
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print("completed")
    else:
        # Print if there are no new alerts
        print("No new alerts")
    # Wait for 60 seconds before checking again
    time.sleep(60)
