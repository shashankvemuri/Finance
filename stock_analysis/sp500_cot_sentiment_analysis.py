# Import dependencies
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import zipfile
import urllib.request
import shutil
import os

def download_and_extract_cot_file(url, file_name):
    """
    Download and extract COT files from the given URL and save them with the given file name.
    """
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(request) as response, open(file_name, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    with zipfile.ZipFile(file_name) as zf:
        zf.extractall()

# Create an empty list to store data frames
frames = []

this_year = datetime.datetime.now().year

# Loop through last 5 years of data
for year in range(this_year-5, this_year+1):
    # Download and extract COT files for the year
    download_and_extract_cot_file(
        f'https://www.cftc.gov/files/dea/history/fut_fin_xls_{year}.zip', f'{year}.zip'
    )
    # Rename the extracted file
    os.rename('FinFutYY.xls', f'{year}.xls')

    # Read the data from the renamed  vfile
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

    # Select only the data for the E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE
    data = data.loc[data['Market_and_Exchange_Names'] == 'E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE']

    # Append the data frame to the frames list
    frames.append(data)

# Concatenate the frames list into a single data frame
df = pd.concat(frames)

# Save the data frame to a CSV file
df.to_csv('COT_sp500_data.csv')

# Read the CSV file into a new data frame with the index as the first column
df = pd.read_csv('COT_sp500_data.csv', index_col=0)
df.index = pd.to_datetime(df.index)

# Assign columns to new variable names for easier referencing
dealer_long_percent = df['Pct_of_OI_Dealer_Long_All']
dealer_short_percent = df['Pct_of_OI_Dealer_Short_All']
lev_long_percent = df['Pct_of_OI_Lev_Money_Long_All']
lev_short_percent = df['Pct_of_OI_Lev_Money_Short_All']

# Line Chart
plt.plot(df.index, dealer_long_percent, label='Dealer Long')
plt.plot(df.index, lev_long_percent, label='Leveraged Long')
plt.plot(df.index, dealer_short_percent, label='Dealer Short')
plt.plot(df.index, lev_short_percent, label='Leveraged Short')
plt.xlabel('Date')
plt.ylabel('Percentage')
plt.title('Net Positions - Line Chart')
plt.legend()
plt.tight_layout()
plt.show()

# Box Plot
boxplot = plt.boxplot([df['Pct_of_OI_Dealer_Long_All'], df['Pct_of_OI_Dealer_Short_All'], df['Pct_of_OI_Lev_Money_Long_All'], df['Pct_of_OI_Lev_Money_Short_All']],
                      labels=['Dealer Long', 'Dealer Short', 'Leveraged Money Long', 'Leveraged Money Short'],
                      patch_artist=True)

current_values = [df['Pct_of_OI_Dealer_Long_All'].iloc[-1], df['Pct_of_OI_Dealer_Short_All'].iloc[-1],
                  df['Pct_of_OI_Lev_Money_Long_All'].iloc[-1], df['Pct_of_OI_Lev_Money_Short_All'].iloc[-1]]

# Add markers for current values
for i, box in enumerate(boxplot['boxes']):
    box.set_facecolor('lightblue')
    plt.text(i + 1, current_values[i], f"{current_values[i]:.2f}", ha='center', va='bottom')

plt.title('Distribution of Open Interest by Category')
plt.ylabel('Percentage')
plt.grid(True)
plt.show()