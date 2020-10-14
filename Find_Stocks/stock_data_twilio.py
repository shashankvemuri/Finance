from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from yahoo_fin import stock_info as si
import pandas as pd
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen

app = Flask(__name__)

@app.route('/sms', methods = ['POST'])
def sms():
    try:
        number = request.form['From']
        message_body = request.form['Body']
        resp = MessagingResponse()
        
        stock = message_body
        
        # price 
        price = si.get_live_price('{}'.format(message_body))
        price = round(price, 2)

        AvgGain= 15
        AvgLoss= 5

        maxStopBuy=round(price*((100-AvgLoss)/100), 2)
        Target1RBuy=round(price*((100+AvgGain)/100),2)
        Target2RBuy=round(price*(((100+(2*AvgGain))/100)),2)
        Target3RBuy=round(price*(((100+(3*AvgGain))/100)),2)

        maxStopShort=round(price*((100+AvgLoss)/100), 2)
        Target1RShort=round(price*((100-AvgGain)/100),2)
        Target2RShort=round(price*(((100-(2*AvgGain))/100)),2)
        Target3RShort=round(price*(((100-(3*AvgGain))/100)),2)

        change = str(round(((price-price)/price)*100, 4)) + '%'
        
        # Set up scraper
        url = (f"https://finviz.com/screener.ashx?v=152&ft=4&t={stock}&ar=180&c=1,2,3,4,5,6,7,14,17,18,23,26,27,28,29,42,43,44,45,46,47,48,49,51,52,53,54,57,58,59,60,62,63,64,67,68,69")
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        html = soup(webpage, "html.parser")

        stocks = pd.read_html(str(html))[-2]
        stocks.columns = stocks.iloc[0]
        stocks = stocks[1:]
        stocks['Price'] = [f'{price}']
        stocks['Change'] = [f'{change}']
        stocks['Risk 1 Buy'] = [f'{Target1RBuy}']
        stocks['Risk 2 Buy'] = [f'{Target2RBuy}']
        stocks['Risk 3 Buy'] = [f'{Target3RBuy}']
        stocks['Max Stop Buy'] = [f'{maxStopBuy}']
        stocks['Risk 1 Short'] = [f'{Target1RShort}']
        stocks['Risk 2 Short'] = [f'{Target2RShort}']
        stocks['Risk 3 Short'] = [f'{Target3RShort}']
        stocks['Max Stop Short'] = [f'{maxStopShort}']
        # stocks['Resistance 1'] = [f'{}']
        # stocks['Resistance 2'] = [f'{}']
        # stocks['Resistance 3'] = [f'{}']
        # stocks['Pivot'] = [f'{}']
        # stocks['Support 1'] = [f'{}']
        # stocks['Support 2'] = [f'{}']
        # stocks['Support 3'] = [f'{}']
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
