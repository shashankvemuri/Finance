import nexmo
from yahoo_fin import stock_info as si

ticker = 'AAPL'
want_price = 322

price = si.get_live_price(ticker)
price = round(price, 2)

if price > want_price:
    client = nexmo.Client(key='19248f09', secret='cryUpv5JsufkO4Xn')
    client.send_message({'from': 14256207607, 'to': 18482521431, 'text': '{} is now above {}, it is {}'.format(ticker, want_price, price)})
else: 
    print ("want price not met")