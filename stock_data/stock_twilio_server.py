# Import dependencies
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from yahoo_fin import stock_info as si
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import pandas as pd

app = Flask(__name__)

@app.route('/sms', methods=['POST'])
def sms():
    try:
        # Get request parameters
        number = request.form['From']
        message_body = request.form['Body']
        
        # Initialize Twilio messaging response
        resp = MessagingResponse()

        # Get stock symbol from message body
        stock_symbol = message_body.upper()
        
        # Get live price of the stock
        price = si.get_live_price(stock_symbol)
        price = round(price, 2)
        
        # Calculate buy and short targets
        avg_gain = 15
        avg_loss = 5
        
        max_stop_buy = round(price * ((100 - avg_loss) / 100), 2)
        target_1r_buy = round(price * ((100 + avg_gain) / 100), 2)
        target_2r_buy = round(price * ((100 + (2 * avg_gain)) / 100), 2)
        target_3r_buy = round(price * ((100 + (3 * avg_gain)) / 100), 2)
        
        max_stop_short = round(price * ((100 + avg_loss) / 100), 2)
        target_1r_short = round(price * ((100 - avg_gain) / 100), 2)
        target_2r_short = round(price * ((100 - (2 * avg_gain)) / 100), 2)
        target_3r_short = round(price * ((100 - (3 * avg_gain)) / 100), 2)

        change = str(round(((price - price) / price) * 100, 4)) + '%'
        
        # Scrape stock data from finviz.com
        url = f"https://finviz.com/screener.ashx?v=152&ft=4&t={stock_symbol}&ar=180&c=1,2,3,4,5,6,7,14,17,18,23,26,27,28,29,42,43,44,45,46,47,48,49,51,52,53,54,57,58,59,60,62,63,64,67,68,69"
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        html = BeautifulSoup(webpage, "html.parser")

        stocks = pd.read_html(str(html))[-2]
        stocks.columns = stocks.iloc[0]
        stocks = stocks[1:]
        stocks['Price'] = [f'{price}']
        stocks['Change'] = [f'{change}']
        stocks['Risk 1 Buy'] = [f'{target_1r_buy}']
        stocks['Risk 2 Buy'] = [f'{target_2r_buy}']
        stocks['Risk 3 Buy'] = [f'{target_3r_buy}']
        stocks['Max Stop Buy'] = [f'{max_stop_buy}']
        stocks['Risk 1 Short'] = [f'{target_1r_short}']
        stocks['Risk 2 Short'] = [f'{target_2r_short}']
        stocks['Risk 3 Short'] = [f'{target_3r_short}']
        stocks['Max Stop Short'] = [f'{max_stop_short}']
        message = "\n"
        for attr, val in zip(stocks.columns, stocks.iloc[0]):
            message=message + f"{attr} : {val}\n"

        resp.message(message)
        return str(resp)
    
    except Exception as e:
        resp.message(f'\n{e}')
        return str(resp)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
