import pandas as pd
import matplotlib.pyplot as plt
import datetime
import zipfile
import urllib.request
import shutil
import os

# Function to download and extract COT file
def download_and_extract_cot_file(url, file_name):
    # Download and extract COT file
    with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    with zipfile.ZipFile(file_name) as zf:
        zf.extractall()

# Download and process COT data for the last 5 years
frames = []
this_year = datetime.datetime.now().year

for year in range(this_year-5, this_year+1):
    url = f'https://www.cftc.gov/files/dea/history/fut_fin_xls_{year}.zip'
    download_and_extract_cot_file(url, f'{year}.zip')
    os.rename('FinFutYY.xls', f'{year}.xls')

    data = pd.read_excel(f'{year}.xls')
    data = data.set_index('Report_Date_as_MM_DD_YYYY')
    data.index = pd.to_datetime(data.index)
    data = data[data['Market_and_Exchange_Names'] == 'E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE']
    frames.append(data)

# Concatenate yearly data frames
df = pd.concat(frames)
df.to_csv('COT_sp500_data.csv')

# Read data for plotting
df = pd.read_csv('COT_sp500_data.csv', index_col=0)
df.index = pd.to_datetime(df.index)

# Plotting
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['Pct_of_OI_Dealer_Long_All'], label='Dealer Long')
plt.plot(df.index, df['Pct_of_OI_Lev_Money_Long_All'], label='Leveraged Long')
plt.plot(df.index, df['Pct_of_OI_Dealer_Short_All'], label='Dealer Short')
plt.plot(df.index, df['Pct_of_OI_Lev_Money_Short_All'], label='Leveraged Short')
plt.xlabel('Date')
plt.ylabel('Percentage')
plt.title('Net Positions - Line Chart')
plt.legend()
plt.tight_layout()
plt.show()

# Box Plot
plt.figure(figsize=(10, 6))
box_data = [df[col] for col in ['Pct_of_OI_Dealer_Long_All', 'Pct_of_OI_Dealer_Short_All', 'Pct_of_OI_Lev_Money_Long_All', 'Pct_of_OI_Lev_Money_Short_All']]
plt.boxplot(box_data, labels=['Dealer Long', 'Dealer Short', 'Leveraged Money Long', 'Leveraged Money Short'], patch_artist=True)
plt.title('Distribution of Open Interest by Category')
plt.ylabel('Percentage')
plt.grid(True)
plt.show()