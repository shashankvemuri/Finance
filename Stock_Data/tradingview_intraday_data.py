# Import dependencies
from websocket import create_connection
import json
import random
import string
import re
import pandas as pd
import csv
import datetime

# Define function to filter relevant data from websocket messages
def filter_raw_message(text):
    try:
        found = re.search('"m":"(.+?)",', text).group(1)
        found2 = re.search('"p":(.+?"}"])}', text).group(1)
        # Print the filtered data for debugging purposes
        print(found)
        print(found2)
        return found, found2
    except AttributeError:
        print("error")

# Define function to generate a random session ID
def generateSession():
    stringLength=12
    letters = string.ascii_lowercase
    random_string= ''.join(random.choice(letters) for i in range(stringLength))
    return "qs_" +random_string

# Define function to generate a random chart session ID
def generateChartSession():
    stringLength=12
    letters = string.ascii_lowercase
    random_string= ''.join(random.choice(letters) for i in range(stringLength))
    return "cs_" +random_string

# Define function to prepend the header required by the websocket
def prependHeader(st):
    return "~m~" + str(len(st)) + "~m~" + st

# Define function to construct the JSON message to be sent over the websocket
def constructMessage(func, paramList):
    return json.dumps({
        "m":func,
        "p":paramList
        }, separators=(',', ':'))

# Define function to create a full message with header and JSON payload
def createMessage(func, paramList):
    return prependHeader(constructMessage(func, paramList))

# Define function to send a raw message over the websocket
def sendRawMessage(ws, message):
    ws.send(prependHeader(message))

# Define function to send a full message with header and JSON payload
def sendMessage(ws, func, args):
    ws.send(createMessage(func, args))

# Define function to extract data from websocket message and save to CSV file
def generate_csv(a):
    out= re.search('"s":\[(.+?)\}\]', a).group(1)
    x=out.split(',{\"')
    
    with open('data_file.csv', mode='w', newline='') as data_file:
        employee_writer = csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    
        # Write CSV header row
        employee_writer.writerow(['index', 'date', 'open', 'high', 'low', 'close', 'volume'])
        
        # Write CSV data rows
        for xi in x:
            xi= re.split('\[|:|,|\]', xi)
            ind= int(xi[1])
            ts= datetime.fromtimestamp(float(xi[4])).strftime("%Y/%m/%d, %H:%M:%S")
            employee_writer.writerow([ind, ts, float(xi[5]), float(xi[6]), float(xi[7]), float(xi[8]), float(xi[9])])

# Initialize the headers needed for the websocket connection
headers = json.dumps({
    'Origin': 'https://data.tradingview.com'
})
    
# Then create a connection to the websocket
ws = create_connection(
    'wss://data.tradingview.com/socket.io/websocket',headers=headers)

# Generate random session and chart session IDs
session= generateSession()
print("session generated {}".format(session))

chart_session= generateChartSession()
print("chart_session generated {}".format(chart_session))

# Send various messages to establish the websocket connection and start streaming data
sendMessage(ws, "set_auth_token", ["unauthorized_user_token"])
sendMessage(ws, "chart_create_session", [chart_session, ""])
sendMessage(ws, "quote_create_session", [session])
sendMessage(ws,"quote_set_fields", [session,"ch","chp","current_session","description","local_description","language","exchange","fractional","is_tradable","lp","lp_time","minmov","minmove2","original_name","pricescale","pro_name","short_name","type","update_mode","volume","currency_code","rchp","rtc"])
sendMessage(ws, "quote_add_symbols",[session, "NASDAQ:AAPL", {"flags":['force_permission']}])
sendMessage(ws, "quote_fast_symbols", [session,"NASDAQ:AAPL"])
sendMessage(ws, "resolve_symbol", [chart_session,"symbol_1","={\"symbol\":\"NASDAQ:AAPL\",\"adjustment\":\"splits\",\"session\":\"extended\"}"])
sendMessage(ws, "create_series", [chart_session, "s1", "s1", "symbol_1", "1", 5000])

# Printing all the results
data = ""
while True:
    try:
        result = ws.recv()
        data=data+result+"\n"
        print(result)
    except Exception as e:
        print(e)
        break

# Generate the csv
generate_csv(data)