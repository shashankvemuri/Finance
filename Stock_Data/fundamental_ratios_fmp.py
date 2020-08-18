import FundamentalAnalysis as fa
import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
from config import financial_model_prep

yf.pdr_override()
# api_key = financial_model_prep()

# #Nasdaq Index components' stocks
# ticker_list = ['TMUSR', 'AAPL', 'MSFT', 'AMZN', 'FB', 'GOOGL', 'GOOG', 'INTC', 'NVDA', 'ADBE',
#                'PYPL', 'CSCO', 'NFLX', 'PEP', 'TSLA', 'CMCSA', 'AMGN', 'COST', 'TMUS', 'AVGO',
#                'TXN', 'CHTR', 'QCOM', 'GILD', 'SBUX', 'INTU', 'VRTX', 'MDLZ', 'ISRG', 'FISV',
#                'BKNG', 'ADP', 'REGN', 'ATVI', 'AMD', 'JD', 'MU', 'AMAT', 'ILMN', 'ADSK',
#                'CSX', 'MELI', 'LRCX', 'ADI', 'ZM', 'BIIB', 'EA', 'KHC', 'WBA', 'LULU',
#                'EBAY', 'MNST', 'DXCM', 'EXC', 'BIDU', 'XEL', 'WDAY', 'DOCU', 'SPLK', 'ORLY',
#                'NXPI', 'CTSH', 'KLAC', 'SNPS', 'SGEN', 'ASML', 'IDXX', 'CSGP', 'CTAS', 'VRSK',
#                'MAR', 'CDNS', 'PAYX', 'ALXN', 'MCHP', 'SIRI', 'ANSS', 'VRSN', 'FAST', 'BMRN',
#                'XLNX', 'INCY','DLTR', 'SWKS', 'ALGN', 'CERN', 'CPRT', 'CTXS', 'TTWO', 'MXIM',
#                'CDW', 'CHKP', 'WDC', 'ULTA', 'NTAP', 'FOXA', 'LBTYK']

# #download financial indicators data and output as excel files
# for ticker in ticker_list:
#     key_metrics_annually = fa.key_metrics(ticker, api_key, period="annual")
#     writer1 = pd.ExcelWriter('/Users/shashank/Documents/Code/Python/Outputs/fundamentals/key_metrics.xlsx')
#     key_metrics_annually.to_excel(writer1, ticker)
        
#     financial_ratios_annually = fa.financial_ratios(ticker, api_key, period="annual")
#     writer2 = pd.ExcelWriter('/Users/shashank/Documents/Code/Python/Outputs/fundamentals/financial_ratios.xlsx')
#     financial_ratios_annually.to_excel(writer2, ticker)

# writer1.save()
# writer2.save()

# data = pdr.get_data_yahoo(ticker_list, start="2017-01-01")
# price = data.loc[:, 'Close']
# price.to_excel("price.xlsx")

df = pd.read_excel('/Users/shashank/Documents/Code/Python/Outputs/fundamentals/key_metrics.xlsx', sheet_name='AAPL')
print (df)