# Import dependencies
import pandas as pd
import matplotlib.pyplot as plt
import zipfile
import urllib.request
import shutil
import os
from pylab import rcParams

# Set pandas display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Set matplotlib figure size
rcParams['figure.figsize'] = (15, 10)

def download_and_extract_cot_file(url, file_name):
    """
    Download and extract COT files from the given URL and save them with the given file name.
    """
    with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    with zipfile.ZipFile(file_name) as zf:
        zf.extractall()


# Create an empty list to store data frames
frames = []

# Loop through years from 2010 to 2020 and extract data
for year in range(2010, 2021):
    # Download and extract COT files for the year
    download_and_extract_cot_file(
        f'https://www.cftc.gov/files/dea/history/fut_fin_xls_{year}.zip', f'{year}.zip'
    )
    # Rename the extracted file
    os.rename('FinFutYY.xls', f'{year}.xls')

    # Read the data from the renamed file
    data = pd.read_excel(f'{year}.xls')

    # Select relevant columns
    data = data[
        [
            'Market_and_Exchange_Names',
            'Report_Date_as_MM_DD_YYYY',
            'Pct_of_OI_Dealer_Long_All',
            'Pct_of_OI_Dealer_Short_All',
            'Pct_of_OI_Lev_Money_Long_All',
            'Pct_of_OI_Lev_Money_Short_All',
        ]
    ]

    # Set the index as the report date and convert to datetime format
    data = data.set_index('Report_Date_as_MM_DD_YYYY')
    data.index = pd.to_datetime(data.index)

    # Reverse the data frame
    data = data.iloc[::-1]

    # Select only the data for the S&P 500 STOCK INDEX - CHICAGO MERCANTILE EXCHANGE
    data = data.loc[data['Market_and_Exchange_Names'] == 'S&P 500 STOCK INDEX - CHICAGO MERCANTILE EXCHANGE']

    # Append the data frame to the frames list
    frames.append(data)

# Concatenate the frames list into a single data frame
df = pd.concat(frames)

# Save the data frame to a CSV file
df.to_csv('COT_sp500_data.csv')

# Read the CSV file into a new data frame with the index as the first column
df = pd.read_csv('COT_sp500_data.csv', index_col=0)

# Assign columns to new variable names for easier referencing
dealer_long_percent = df['Pct_of_OI_Dealer_Long_All']
dealer_short_percent = df['Pct_of_OI_Dealer_Short_All']
lev_long_percent = df['Pct_of_OI_Lev_Money_Long_All']
lev_short_percent = df['Pct_of_OI_Lev_Money_Short_All']

# Calculate the total percentage of shorts and longs
total_short_percent = df['Pct_of_OI_Dealer_Short_All'] + df['Pct_of_OI_Lev_Money_Short_All']
total_long_percent = df['Pct_of_OI_Dealer_Long_All'] + df['Pct_of_OI_Lev_Money_Long_All']

# Plot Dealer and Leverage Long/Short Percentages
ax = df['Pct_of_OI_Dealer_Long_All'].plot()
df['Pct_of_OI_Dealer_Short_All'].plot(ax=ax)
df['Pct_of_OI_Lev_Money_Long_All'].plot(ax=ax)
df['Pct_of_OI_Lev_Money_Short_All'].plot(ax=ax)
plt.legend()
plt.title('Dealer and Leverage Long/Short Percentage')
plt.grid()
plt.show()

# Longs vs Shorts
plt.subplots()
ax = total_long_percent.plot()
total_short_percent.plot(ax=ax)
plt.legend(['Longs', 'Shorts'])
plt.title('Longs vs. Shorts')
plt.grid()
plt.show()

# Total Long Percent
plt.subplots()
plt.plot(total_long_percent)
plt.legend(['Longs'])
plt.title('Longs')
plt.show()

# Total Short Percent
plt.subplots()
plt.plot(total_short_percent)
plt.legend(['Shorts'])
plt.title('Shorts')
plt.show()