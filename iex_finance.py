from iexfinance.stocks import get_historical_data
from datetime import datetime
import os

start = datetime(2019, 1, 1)
end = datetime.now()

os.environ['IEX_TOKEN'] = ""

df = get_historical_data("AAPL", start=start, end=end, output_format="pandas")
