# Import required modules
import requests
import pandas as pd
from config import financial_model_prep

# Create an instance of the financial model prep class
demo = financial_model_prep()

# Read ticker symbols from pickle file
symbols = pd.read_pickle('spxTickers.pickle')

# Initialize an empty dictionary to store dividend yield data
yield_dict = {}

# Loop through the ticker symbols
for company in symbols:
  try:
    # Get the company data using FMP API and the financial model prep instance
    companydata = requests.get(f'https://fmpcloud.io/api/v3/profile/{company}?apikey={demo}')
    # Convert the company data to a JSON format
    companydata = companydata.json()
    
    # Extract relevant data from the JSON response
    latest_Annual_Dividend = companydata[0]['lastDiv']
    price = companydata[0]['price']
    market_Capitalization = companydata[0]['mktCap']
    name = companydata[0]['companyName']
    exchange = companydata[0]['exchange']

    # Calculate the dividend yield and store the data in the yield_dict dictionary
    dividend_yield= latest_Annual_Dividend/price
    yield_dict[company] = {}
    yield_dict[company]['dividend_yield'] = yield_dict
    yield_dict[company]['latest_price'] = price
    yield_dict[company]['latest_dividend'] = latest_Annual_Dividend
    yield_dict[company]['market_cap'] = market_Capitalization/1000000
    yield_dict[company]['company_name'] = name
    yield_dict[company]['exchange'] = exchange
  except:
    # If an error occurs, continue to the next ticker symbol
    pass

# Create a pandas DataFrame from the yield_dict dictionary and sort it by dividend yield in descending order
yield_dataframe = pd.DataFrame.from_dict(yield_dict, orient='index')
yield_dataframe = yield_dataframe.sort_values('dividend_yield', ascending=False)

# Print the DataFrame
print(yield_dataframe)