import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import warnings
warnings.filterwarnings("ignore") 
import yfinance as yf
yf.pdr_override()
import datetime as dt
from scipy.stats import linregress
from scipy import stats


symbol = 'AMD'
market = 'SPY'

num_of_years = 3
start = dt.date.today() - dt.timedelta(days=365*num_of_years)
end = dt.date.today()

dataset = yf.download(symbol,start,end)
benchmark = yf.download(market,start,end)

dataset['Returns'] = dataset['Adj Close'].pct_change().dropna()
max_r = dataset['Adj Close'].max()
min_r = dataset['Adj Close'].min()
avg_r = dataset['Adj Close'].mean()

y = [min_r, avg_r, max_r]


plt.figure(figsize=(12,8))
plt.plot(dataset['Adj Close'], color='green')
plt.title(symbol + ' Closing Price', fontsize=18, fontweight='bold')
plt.ylabel('Price')
plt.xlabel('Date')
plt.legend()
plt.show()

benchmark['Normalize'] = benchmark['Adj Close']/benchmark['Adj Close'][0]
dataset['Normalize'] = dataset['Adj Close']/dataset['Adj Close'][0]

plt.figure(figsize=(12,8))
plt.plot(benchmark['Adj Close'], color='red', label=market)
plt.plot(dataset['Adj Close'], color='green', label=symbol)
plt.title('Compare Stock Closing Price')
plt.legend(loc='best')
plt.show()

plt.figure(figsize=(12,8))
plt.plot(benchmark['Normalize'], color='red', label=market)
plt.plot(dataset['Normalize'], color='green', label=symbol)
plt.title("Compare Normalize of Stock and SPY")
plt.legend(loc='best')
plt.show()

dataset['Max5'] = dataset['Adj Close'].rolling(5).max()
dataset['Min5'] = dataset['Adj Close'].rolling(5).min()
dataset['Avg5'] = dataset['Adj Close'].rolling(5).mean()

plt.figure(figsize=(20,12))
plt.plot(dataset['Max5'],'go')
plt.plot(dataset['Min5'],'ro')
plt.plot(dataset['Avg5'],'yo')
plt.plot(dataset['Adj Close'], color='blue', label=symbol)
plt.show()

print(dataset['Adj Close'].count())

max_price = dataset['Adj Close'].max()
print(max_price)
min_price = dataset['Adj Close'].min()
print(min_price)
avg_price = dataset['Adj Close'].mean()
print(avg_price)
median_price = dataset['Adj Close'].median()
print(median_price)
mode_price = dataset['Adj Close'].mode()
print(mode_price)

dataset['Adj Close'][dataset['Adj Close'] == max_price].index
dataset.index = pd.to_datetime(dataset.index)

adj_close = dataset[['Adj Close']].reset_index()
adj_close_max = adj_close[['Date', 'Adj Close']].max()

plt.figure(figsize=(20,10))
plt.plot(dataset['Adj Close'].idxmax(), dataset['Adj Close'].max(), 'ro', label='Highest Point')
plt.plot(dataset['Adj Close'].idxmin(), dataset['Adj Close'].min(), 'go', label='Lowest Point')
plt.plot(dataset['Adj Close'], color='blue')
plt.title('Stock Price')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend(loc='best')
plt.show()

def connectpoints():
    x1, x2 = dataset['Adj Close'].idxmin(), dataset['Adj Close'].idxmax()
    y1, y2 = dataset['Adj Close'].min(), dataset['Adj Close'].max()
    plt.plot([x1,x2],[y1,y2],'k-')
    return


plt.figure(figsize=(20,10))
plt.plot(dataset['Adj Close'].idxmax(), dataset['Adj Close'].max(), 'ro', label='Highest Point')
plt.plot(dataset['Adj Close'].idxmin(), dataset['Adj Close'].min(), 'go', label='Lowest Point')
plt.plot(dataset['Adj Close'], color='blue')
connectpoints()
plt.title('Stock Price')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend(loc='best')
plt.show()

midpoint = (dataset['Adj Close'].max() + dataset['Adj Close'].min())/2
# Find Midpoint Date
midpoint_date = dataset['Adj Close'].idxmin() + (dataset['Adj Close'].idxmax() - dataset['Adj Close'].idxmin())/2

plt.figure(figsize=(20,10))
plt.plot(midpoint_date, dataset['Adj Close'].loc['2018-06-22'],'go', label='Midpoint')
plt.plot(dataset['Adj Close'], color='blue')
plt.title('Stock Price')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend(loc='best')
plt.show()

Avg_Price = dataset['Adj Close'].mean()
dataset.loc[dataset['Adj Close'] == 8.16] # Does not have 8.16
dataset.loc[dataset['Adj Close'] == 15.80] 

plt.figure(figsize=(20,10))
plt.hlines(dataset['Adj Close'].mean(), xmin=dataset.index[0], xmax=dataset.index[-1], linewidth=2, label='Mean', linestyle='--')
plt.hlines(dataset['Adj Close'].median(), xmin=dataset.index[0], xmax=dataset.index[-1], color='y', label='Median', linestyle='--')
plt.hlines(dataset['Adj Close'].mode(), xmin=dataset.index[0], xmax=dataset.index[-1], color='orange', label='Mode', linestyle='--')
plt.plot(dataset['Adj Close'].idxmax(), dataset['Adj Close'].max(), 'ro', label='Highest Point')
plt.plot(dataset['Adj Close'].idxmin(), dataset['Adj Close'].min(), 'go', label='Lowest Point')
plt.plot(dataset['Adj Close'], color='blue')
plt.title('Stock Price')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend(loc='best')
plt.show()

slope, intercept, r_value, p_value, std_err = stats.linregress(benchmark['Adj Close'], dataset['Adj Close'])
print("slope: %f    intercept: %f" % (slope, intercept))
print("R-squared: %f" % r_value**2)
print("p-value: %f" % p_value)

X2 = np.linspace(benchmark['Adj Close'].min(), benchmark['Adj Close'].max(), 100)
Y_hat = X2 * slope + intercept 

plt.scatter(benchmark['Adj Close'].values, dataset['Adj Close'].values, alpha=0.3, label='Stock data')
plt.plot(X2, Y_hat, 'r', label='fitted line')
plt.title("CAPM")
plt.legend()
plt.show()

coefficients, residuals, _, _, _ = np.polyfit(range(len(dataset.index)), dataset['Adj Close'],1, full=True)

mse = residuals[0]/(len(dataset.index))
nrmse = np.sqrt(mse)/(dataset['Adj Close'].max() - dataset['Adj Close'].min())
print('Slope ' + str(coefficients[0]))
print('Normalized Mean Squared Error (NRMSE): ' + str(nrmse))

plt.figure(figsize=(16,10))
plt.plot(dataset['Adj Close'].values, label='Price')
plt.plot([coefficients[0]*x + coefficients[1] for x in range(len(dataset))], label='Trendline')
plt.title('Stock and Trendline')
plt.legend(loc='best')
plt.show()


data = dataset.copy()
#data = pd.to_datetime(data.index)
data['date_id'] = ((data.index.date - data.index.date.min()))
data['date_id'] = data['date_id'].dt.days + 1

data1 = data.copy()
while len(data1)>3:
    reg = linregress(
                    x=data1['date_id'],
                    y=data1['High'],
                    )
    data1 = data1.loc[data1['High'] > reg[0] * data1['date_id'] + reg[1]]
reg = linregress(
                    x=data1['date_id'],
                    y=data1['High'],
                    )

data['High_Trend'] = reg[0] * data['date_id'] + reg[1]
data1 = data.copy()


while len(data1)>3:
    reg = linregress(
                    x=data1['date_id'],
                    y=data1['Low'],
                    )
    data1 = data1.loc[data1['Low'] < reg[0] * data1['date_id']+ reg[1]]
reg = linregress(
                    x=data1['date_id'],
                    y=data1['Low'],
                    )
data['Low_Trend'] = reg[0] * data['date_id'] + reg[1]

data[['Adj Close', 'Low_Trend','High_Trend']].plot(figsize=(16,10))
plt.xlabel('Price')
plt.title('Stock Trendlines')
plt.show()


data['Trendline'] = [coefficients[0]*x + coefficients[1] for x in range(len(dataset))]
data[['Adj Close', 'Low_Trend','High_Trend','Trendline']].plot(figsize=(16,10))
plt.title('Stock Trendlines')
plt.ylabel('Price')
plt.show()

PP = pd.Series((dataset['High'] + dataset['Low'] + dataset['Close']) / 3)  
R1 = pd.Series(2 * PP - dataset['Low'])  
S1 = pd.Series(2 * PP - dataset['High'])  
R2 = pd.Series(PP + dataset['High'] - dataset['Low'])  
S2 = pd.Series(PP - dataset['High'] + dataset['Low'])  
R3 = pd.Series(dataset['High'] + 2 * (PP - dataset['Low']))  
S3 = pd.Series(dataset['Low'] - 2 * (dataset['High'] - PP))
R4 = pd.Series(dataset['High'] + 3 * (PP - dataset['Low']))  
S4 = pd.Series(dataset['Low'] - 3 * (dataset['High'] - PP))
R5 = pd.Series(dataset['High'] + 4 * (PP - dataset['Low']))  
S5 = pd.Series(dataset['Low'] - 4 * (dataset['High'] - PP))
P = pd.Series((dataset['Open'] + (dataset['High'] + dataset['Low'] + dataset['Close'])) / 4) # Opening Price Formula
psr = {'P':P, 'R1':R1, 'S1':S1, 'R2':R2, 'S2':S2, 'R3':R3, 'S3':S3,'R4':R4, 'S4':S4,'R5':R5, 'S5':S5}  
PSR = pd.DataFrame(psr)  
dataset = dataset.join(PSR)
print(dataset.head())

pivot_point = pd.concat([dataset['Adj Close'],P,R1,S1,R2,S2,R3,S3],axis=1).plot(figsize=(18,12),grid=True)
plt.title('Stock Pivot Point')
plt.legend(['Price','P','R1','S1','R2','S2','R3','S3'], loc=0)
plt.show()

dataset['Adj Close']['2018-05-01':'2018-06-01']
date_range = dataset[['Adj Close','P','R1','S1','R2','S2','R3','S3']]['2018-05-01':'2018-06-01']# Pick Date Ranges
date_range.plot(figsize=(18,12),grid=True)
plt.title('Stock Pivot Point')
plt.legend(['Price','P','R1','S1','R2','S2','R3','S3'], loc=0)
plt.show()

ax = date_range.plot(figsize=(18,12), grid=True) 
ax.lines[0].set_linewidth(4) # Plot Specific Line, 0 represent the first line that is Adj Close and 4 is how thick the line you want to be
plt.title('Stock Pivot Point')
plt.legend()
plt.show()

date_range.plot(figsize=(18,12),grid=True)
plt.hlines(date_range['R1'].mean(), xmin=dataset.index[0], xmax=dataset.index[-1], color='orange', label='Resistance 1', linestyle='--', lw=2)
plt.hlines(date_range['S1'].mean(), xmin=dataset.index[0], xmax=dataset.index[-1], color='orange', label='Support 1', linestyle='--', lw=2)
plt.hlines(date_range['R2'].mean(), xmin=dataset.index[0], xmax=dataset.index[-1], color='red', label='Resistance 2', linestyle='--', lw=2)
plt.hlines(date_range['S2'].mean(), xmin=dataset.index[0], xmax=dataset.index[-1], color='red', label='Support 2', linestyle='--', lw=2)
plt.hlines(date_range['R3'].mean(), xmin=dataset.index[0], xmax=dataset.index[-1], color='pink', label='Resistance 3', linestyle='--', lw=2)
plt.hlines(date_range['S3'].mean(), xmin=dataset.index[0], xmax=dataset.index[-1], color='pink', label='Support 3', linestyle='--', lw=2)
plt.title('Stock Pivot Point Line')
plt.legend(['Price','P','R1','S1','R2','S2','R3','S3'], loc=0)
plt.show()