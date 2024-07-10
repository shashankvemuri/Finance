# Import necessary libraries
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import pandas_datareader.data as pdr
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import pandas as pd

# Initialize Flask app
app = Flask(__name__)

# Define route for incoming SMS messages
@app.route('/sms', methods=['POST'])
def sms():
    try:
        # Retrieve sender's number and message content
        number = request.form['From']
        message_body = request.form['Body']
        
        # Create a Twilio MessagingResponse object
        resp = MessagingResponse()

        # Extract stock symbol from the message body
        stock_symbol = message_body.upper()
        
        # Fetch the latest adjusted close price of the stock
        df = pdr.get_data_yahoo(stock_symbol)
        price = round(df['Adj Close'][-1], 2)
        
        # Calculate buy and short targets using predetermined percentages
        avg_gain = 15
        avg_loss = 5
        max_stop_buy = round(price * ((100 - avg_loss) / 100), 2)
        target_1r_buy = round(price * ((100 + avg_gain) / 100), 2)
        max_stop_short = round(price * ((100 + avg_loss) / 100), 2)
        target_1r_short = round(price * ((100 - avg_gain) / 100), 2)

        # Additional target calculations
        target_2r_buy = round(price * ((100 + (2 * avg_gain)) / 100), 2)
        target_3r_buy = round(price * ((100 + (3 * avg_gain)) / 100), 2)
        target_2r_short = round(price * ((100 - (2 * avg_gain)) / 100), 2)
        target_3r_short = round(price * ((100 - (3 * avg_gain)) / 100), 2)

        # Calculate the percentage change of the stock price
        change = str(round(((price - price) / price) * 100, 4)) + '%'
        
        # Scrape and parse stock data from finviz.com
        url = f"https://finviz.com/screener.ashx?v=152&ft=4&t={stock_symbol}"
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        html = BeautifulSoup(webpage, "html.parser")

        # Convert scraped HTML to a pandas DataFrame
        stocks = pd.read_html(str(html))[-2]
        # Update DataFrame with calculated data
        stocks.update({'Price': price, 'Change': change, 
                       'Risk 1 Buy': target_1r_buy, 'Risk 2 Buy': target_2r_buy,
                       'Risk 3 Buy': target_3r_buy, 'Max Stop Buy': max_stop_buy,
                       'Risk 1 Short': target_1r_short, 'Risk 2 Short': target_2r_short,
                       'Risk 3 Short': target_3r_short, 'Max Stop Short': max_stop_short})

        # Format the message with stock information
        message = "\n"
        for attr, val in zip(stocks.columns, stocks.iloc[0]):
            message += f"{attr} : {val}\n"

        # Send the formatted message as a response
        resp.message(message)
        return str(resp)
    
    except Exception as e:
        # Handle exceptions and send error message as response
        resp.message(f'\nError: {e}')
        return str(resp)

# Run the Flask app
if __name__ == "__main__":
    app.run(port=5000, debug=True)