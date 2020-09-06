import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import yahoo_fin.stock_info as si
import time
import datetime
from config import *
import os

df = si.get_day_gainers()
df_filtered = df[df['% Change']>=5]

today = datetime.date.today()
file_name = '/Users/shashank/Documents/Code/Python/Outputs/movers/' + "Top Gainers " + str(today) +".csv"
df_filtered.to_csv(file_name)

def send_email():
   email_sender = junk_email_username()
   email_recipient = good_email_username()
   msg = MIMEMultipart()
   email_message = "Attached are today's market movers"
   attachment_location= file_name
   msg['From'] = email_sender
   msg['To'] = email_recipient
   msg['Subject'] = "Stock Market Movers"
   msg.attach(MIMEText(email_message, 'plain'))
   if attachment_location != '':
      filename = os.path.basename(attachment_location)
      attachment = open(attachment_location, 'rb')
      part = MIMEBase('application', 'octet-stream')
      part.set_payload(attachment.read())
      encoders.encode_base64(part)
      part.add_header('Content-Disposition', "attachment; filename=%s" % filename)
      msg.attach(part)
   try:
      server = smtplib.SMTP('smtp.gmail.com', 587)
      server.ehlo()
      server.starttls()
      server.login(junk_email_username(), junk_email_password())
      text = msg.as_string()
      server.sendmail(email_sender, email_recipient, text)
      print('email sent')
      server.quit()
   except Exception as e:
      print(e)
   return schedule.CancelJob

import schedule
schedule.every().day.at("4:00").do(send_email)
while schedule.jobs:
   schedule.run_pending()
   time.sleep(1)