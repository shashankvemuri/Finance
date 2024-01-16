import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import time
import datetime
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import schedule

# Function to scrape top winner stocks from Yahoo Finance
def scrape_top_winners():
    url = 'https://finance.yahoo.com/gainers/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Parse the HTML content and extract data into a DataFrame
    df = pd.read_html(str(soup), attrs={'class': 'W(100%)'})[0]
    # Drop irrelevant columns for simplicity
    df = df.drop(columns=['52 Week High'])
    return df

# Retrieve top gainers data and filter based on a certain percentage change
df = scrape_top_winners()
df_filtered = df[df['% Change'] >= 5]

# Save the filtered DataFrame to a CSV file
today = datetime.date.today()
file_name = "Top Gainers " + str(today) + ".csv"
df_filtered.to_csv(file_name)

# Function to send an email with the top gainers CSV file as an attachment
def send_email():
    # Email sender and recipient details (to be filled)
    email_sender = 'your_email@gmail.com'  # Sender's email
    email_password = 'your_password'  # Sender's email password
    email_recipient = 'recipient_email@gmail.com'  # Recipient's email

    # Email content setup
    msg = MIMEMultipart()
    email_message = "Attached are today's market movers"
    msg['From'] = email_sender
    msg['To'] = email_recipient
    msg['Subject'] = "Stock Market Movers"
    msg.attach(MIMEText(email_message, 'plain'))

    # Attaching the CSV file to the email
    attachment_location = file_name
    if attachment_location != '':
        filename = os.path.basename(attachment_location)
        attachment = open(attachment_location, 'rb')
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename=%s" % filename)
        msg.attach(part)

    # Send the email using SMTP protocol
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(email_sender, email_password)
        text = msg.as_string()
        server.sendmail(email_sender, email_recipient, text)
        print('Email sent successfully.')
        server.quit()
    except Exception as e:
        print(f'Failed to send email: {e}')
    
    return schedule.CancelJob

# Schedule the email to be sent every day at a specific time (e.g., 4:00 PM)
schedule.every().day.at("16:00").do(send_email)

# Run the scheduled task
while True:
    schedule.run_pending()
    time.sleep(1)