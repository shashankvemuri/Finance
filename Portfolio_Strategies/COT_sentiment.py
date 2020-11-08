import pandas as pd
import matplotlib.pyplot as plt
import zipfile, urllib.request, shutil
import os
from pylab import rcParams
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
rcParams['figure.figsize'] = (15, 10)

def get_COT(url, file_name):    
    with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    with zipfile.ZipFile(file_name) as zf:
            zf.extractall()

frames = []
for year in range(2010, 2021, 1):
    # Downloading and extracting COT files
    get_COT(f'https://www.cftc.gov/files/dea/history/fut_fin_xls_{year}.zip',
            f'{year}.zip')
    # Renaming
    os.rename('FinFutYY.xls',
              f'{year}.xls')

    data = pd.read_excel(f'{year}.xls')
    data = data[['Market_and_Exchange_Names', 
                                      'Report_Date_as_MM_DD_YYYY',
                                      'Pct_of_OI_Dealer_Long_All',
                                      'Pct_of_OI_Dealer_Short_All',
                                      'Pct_of_OI_Lev_Money_Long_All',
                                      'Pct_of_OI_Lev_Money_Short_All',]]

    data = data.set_index('Report_Date_as_MM_DD_YYYY')
    data.index = pd.to_datetime(data.index)
    data = data.iloc[::-1]
    data = data.loc[data['Market_and_Exchange_Names'] == 'S&P 500 STOCK INDEX - CHICAGO MERCANTILE EXCHANGE']
    frames.append(data)

df = pd.concat(frames)
df.to_csv('COT_sp500_data.csv')

df = pd.read_csv('COT_sp500_data.csv', index_col=0)
dealer_long = df['Pct_of_OI_Dealer_Long_All']
dealer_short = df['Pct_of_OI_Dealer_Short_All']
lev_long = df['Pct_of_OI_Lev_Money_Long_All']
lev_short = df['Pct_of_OI_Lev_Money_Short_All']

shorts = df['Pct_of_OI_Dealer_Short_All'] + df['Pct_of_OI_Lev_Money_Short_All']
longs = df['Pct_of_OI_Dealer_Long_All'] + df['Pct_of_OI_Lev_Money_Long_All']

ax = df['Pct_of_OI_Dealer_Long_All'].plot()
df['Pct_of_OI_Dealer_Short_All'].plot(ax=ax)
df['Pct_of_OI_Lev_Money_Long_All'].plot(ax=ax)
df['Pct_of_OI_Lev_Money_Short_All'].plot(ax=ax)
plt.legend()
plt.title('Dealer and Leverage Long/Short Percentage')
plt.grid()
plt.show()

plt.subplots()
ax = longs.plot()
shorts.plot(ax=ax)
plt.legend(['Longs', 'Shorts'])
plt.title('Longs vs. Shorts')
plt.grid()
plt.show()

plt.subplots()
plt.plot(longs)
plt.legend(['Longs'])
plt.title('Longs')
plt.show()

plt.subplots()
plt.plot(shorts)
plt.legend(['Shorts'])
plt.title('Shorts')
plt.show()