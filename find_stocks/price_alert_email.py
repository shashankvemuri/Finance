import os
import smtplib
from email.message import EmailMessage
import yfinance as yf
import datetime as dt
from pandas_datareader import data as pdr
import time

# Email credentials from environment variables
EMAIL_ADDRESS = os.environ.get('EMAIL_USER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASS')

# Stock and target price settings
stock = "QQQ"
target_price = 180

# Email setup
msg = EmailMessage()
msg['Subject'] = f'Alert on {stock}!'
msg['From'] = EMAIL_ADDRESS
msg['To'] = 'recipient@example.com'  # Set the recipient email address

# Time settings
start = dt.datetime(2018, 12, 1)
now = dt.datetime.now()

# Initialize alerted flag
alerted = False

# Main loop
while True:
    # Fetch stock data
    df = pdr.get_data_yahoo(stock, start, now)
    current_close = df["Adj Close"][-1]

    # Check if the target price is reached
    if current_close > target_price and not alerted:
        alerted = True
        message = f"{stock} has reached the alert price of {target_price}\nCurrent Price: {current_close}"
        print(message)
        msg.set_content(message)

        # Send email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print("Email sent successfully.")
    else:
        print("No new alerts.")

    # Wait for 60 seconds before the next check
    time.sleep(60)