#data analysis and manipulation
import numpy as np
import pandas as pd
#data visualization
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('whitegrid')

#initializing our data variable as our eMini data
data=pd.read_csv('/Users/shashank/Documents/GitHub/Code/csv/ESPostData.csv')

data.head()

#making copy of our data
es=data.copy()
#creating delta column
es['Delta']=es[' BidVolume']-es[' AskVolume']

#creating regression plot
sns.lmplot('Delta',' Close',data=es)
plt.title('ES Regression Delta to Close')

#creating distribution of delta
sns.distplot(es['Delta'])
plt.title('ES Delta Distribution')

#adding our range column
es['Range']=es[' High']-es[' Low']

#rechecking the head of our data
es.head()

sns.jointplot(es['Delta'], es['Range'])

#creating number of trades distribution
sns.distplot(es[' NumberOfTrades'],bins=100)

class rsi_strategy(object):
 
 def __init__(self,data,n,data_name,start,end):
 
   self.data=data #the dataframe
   self.n=n #the moving average
   self.data_name=data_name #the name that will appear on plots
   self.start=start #the beginning date of the sample period
   self.end=end #the ending date of the sample period
 
def generate_signals(self):
 
   delta=self.data[' Close'].diff()
   dUp,dDown=delta.copy(),delta.copy()
   dUp[dUp<0]=0
   dDown[dDown>0]=0
   RolUp=dUp.rolling(self.n).mean()
   RolDown=dDown.rolling(self.n).mean()

   #assigning indicator to the dataframe
   self.data['RSI']=np.where(RolDown!=0, RolUp/RolDown,1)
   self.data['RSI_Slow']=self.data['RSI'].rolling(self.n).mean()

   #creating signals
   self.data=self.data.assign(Signal=pd.Series(np.zeros(len(self.data))).values)
   self.data.loc[self.data['RSI']<self.data['RSI_Slow'],'Signal']=1
   self.data.loc[self.data['RSI']>self.data['RSI_Slow'], 'Signal']=-1
 
   return
 
def plot_performance(self,allocation):
    #intializing a variable for initial allocation
    #to be used to create equity curve
    self.allocation=allocation
 
    #creating returns and portfolio value series
    self.data['Return']=np.log(self.data[' Close']/self.data[' Close'].shift(1))
    self.data['S_Return']=self.data['Signal'].shift(1)*self.data['Return']
    self.data['Market_Return']=self.data['Return'].expanding().sum()
    self.data['Strategy_Return']=self.data['S_Return'].expanding().sum()
    self.data['Portfolio Value']=((self.data['Strategy_Return']+1)*self.allocation)
 
    #creating metrics
    self.data['Wins']=np.where(self.data['S_Return'] > 0,1,0)
    self.data['Losses']=np.where(self.data['S_Return']<0,1,0)
    self.data['Total Wins']=self.data['Wins'].sum()
    self.data['Total Losses']=self.data['Losses'].sum()
    self.data['Total Trades']=self.data['Total Wins'][0]+self.data['Total Losses'][0]
    self.data['Hit Ratio']=round(self.data['Total Wins']/self.data['Total Losses'],2)
    self.data['Win Pct']=round(self.data['Total Wins']/self.data['Total Trades'],2)
    self.data['Loss Pct']=round(self.data['Total Losses']/self.data['Total Trades'],2)
 
    #Plotting the Performance of the RSI Strategy
 
    plt.plot(self.data['Market_Return'],color='black', label='Market Returns')
    plt.plot(self.data['Strategy_Return'],color='blue', label= 'Strategy Returns')
    plt.title('%s RSI Strategy Backtest'%(self.data_name))
    plt.legend(loc=0)
    plt.tight_layout()
    plt.show()
 
    plt.plot(self.data['Portfolio Value'])
    plt.title('%s Portfolio Value'%(self.data_name))
    plt.show()
    
#creating an instance of our strategy class
strat1=rsi_strategy(es,10,'ES',es['Date'][0],es['Date'].iloc[-1])

#generating signals
strat1.generate_signals()

#plotting performance of our strat1 strategy
#passing in an allocation amount of $10,000
strat1.plot_performance(10000)

#checking our Hit Ratio
strat1.data['Hit Ratio'][0]

#checking our win percentage
print('Strategy Win Percentage')
strat1.data['Win Pct'][0]


#checking our loss percentage
print('Strategy Loss Percentage')
strat1.data['Loss Pct'][0]

#checking total number of wins
strat1.data['Total Wins'][0]

#checking total number of losses
strat1.data['Total Losses'][0]

#checking total number of trades
strat1.data['Total Trades'][0]

from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.metrics import confusion_matrix, classification_report

df=strat1.data

#adding column to hold the direction of returns
df['Return Direction']=np.where(df['Strategy_Return']>0,'Up',np.where(df['Strategy_Return']<0,'Down',"Flat"))

#adding our features
#creating volatility
strat1.data['Vol']=strat1.data[' Close'].rolling(window=5).std()
#creating lags of volatility
strat1.data['Vol Lag 3']=strat1.data['Vol'].shift(3)
strat1.data['Vol Lag 4']=strat1.data['Vol'].shift(4)
strat1.data['Vol Lag 5']=strat1.data['Vol'].shift(5)

#copying our strategy dataframe
df=strat1.data.copy()

#initializing features
X=df[['Vol Lag 3','Vol Lag 4','Vol Lag 5', 'RSI']]

#initialing our response
y=df['Return Direction']

from sklearn.model_selection import train_test_split

#initializing training and testing variables
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2)

model=QuadraticDiscriminantAnalysis()

#fitting model to our training data
#and filling null values with 0
model.fit(X_train.fillna(0),y_train)

QuadraticDiscriminantAnalysis(priors=None, reg_param=0.0,
     store_covariances=False, tol=0.0001)

#creating predictions
predictions=model.predict(X_test.fillna(0))

#initializing confusion matrix
print('Confusion Matrix:')
print(confusion_matrix(y_test,predictions))

#initializing classification report
print('Classification Report')
print(classification_report(y_test,predictions))

#initializing second predictions variable for es dataframe
predictions_2=model.predict(X.fillna(0))

#initializing second predictions variable for es dataframe
predictions_2=model.predict(X.fillna(0))

class optimized_rsi(object):

    def __init__(self,data,n,data_name,start,end):

        self.data=data #the dataframe
        self.n=n #the moving average
        self.data_name=data_name #the name that will appear on plots
        self.start=start #the beginning date of the sample period
        self.end=end #the ending date of the sample period

def generate_signals(self):

    delta=self.data[' Close'].diff()
    dUp,dDown=delta.copy(),delta.copy()
    dUp[dUp<0]=0 
    dDown[dDown>0]=0
    RolUp=dUp.rolling(self.n).mean()
    RolDown=dDown.rolling(self.n).mean()

    #assigning indicator to the dataframe
    self.data['RSI']=np.where(RolDown!=0, RolUp/RolDown,1)
    self.data['RSI_Slow']=self.data['RSI'].rolling(self.n).mean()

    #creating signals;
    #altering the signal generator by going through our predictions
    #and reinitializing signals to 0 whose prediction is down
    self.data=self.data.assign(Signal=pd.Series(np.zeros(len(self.data))).values)
    self.data['QDA Signal']=np.zeros(len(self.data))

    self.data.loc[self.data['RSI']<self.data['RSI_Slow'],'Signal']=1 
    self.data.loc[self.data['RSI']>self.data['RSI_Slow'], 'Signal'] =-1

    self.data['QDA Signal']=np.where(self.data['Predictions']==["Down"],0,self.data['Signal'])

    return

def plot_performance(self,allocation):
    #intializing a variable for initial allocation
    #to be used to create equity curve
    self.allocation=allocation

    #creating returns and portfolio value series
    self.data['Return']=np.log(self.data[' Close']/self.data[' Close'].shift(1))
    #using our signal 2 column to calcuate returns instead of signal 1 column
    self.data['S_Return']=self.data['QDA Signal'].shift(1)*self.data['Return']
    self.data['Market_Return']=self.data['Return'].expanding().sum()
    self.data['Strategy_Return']=self.data['S_Return'].expanding().sum()
    self.data['Portfolio Value']=((self.data['Strategy_Return']+1)*self.allocation)

    #creating metrics
    self.data['Wins']=np.where(self.data['S_Return'] > 0,1,0)
    self.data['Losses']=np.where(self.data['S_Return']<0,1,0)
    self.data['Total Wins']=self.data['Wins'].sum()
    self.data['Total Losses']=self.data['Losses'].sum()
    self.data['Total Trades']=self.data['Total Wins'][0]+self.data['Total Losses'][0]
    self.data['Hit Ratio']=round(self.data['Total Wins']/self.data['Total Losses'],2)
    self.data['Win Pct']=round(self.data['Total Wins']/self.data['Total Trades'],2)
    self.data['Loss Pct']=round(self.data['Total Losses']/self.data['Total Trades'],2)

    #Plotting the Performance of the RSI Strategy

    plt.plot(self.data['Market_Return'],color='black', label='Market Returns')
    plt.plot(self.data['Strategy_Return'],color='blue', label= 'Strategy Returns')
    plt.title('%s RSI Strategy Backtest'%(self.data_name))
    plt.legend(loc=0)
    plt.tight_layout()
    plt.show()

    plt.plot(self.data['Portfolio Value'])
    plt.title('%s Portfolio Value'%(self.data_name))
    plt.show()
    
#initializing our strat2 strategy
strat2=optimized_rsi(es,10,'ES',es.iloc[0]['Date'],es.iloc[-1]['Date'])

#generating signals
strat2.generate_signals()

#plotting performance
strat2.plot_performance(10000)

#generating metrics
strat2_trades=strat2.data['Total Trades'][0]
strat2_hit_ratio=strat2.data['Hit Ratio'][0]
strat2_win_pct=strat2.data['Win Pct'][0]
strat2_loss_pct=strat2.data['Loss Pct'][0]


#printing strat2 metrics
print('Strat 2 Hit Ratio:',strat2_hit_ratio)
print('Strat 2 Win Percentage:',strat2_win_pct)
print('Strat 2 Loss Percentage:',strat2_loss_pct)
print('Strat 2 Total Trades:',strat2_trades)

#getting strat1 metrics
strat1_trades=strat1.data['Total Trades'][0]
strat1_hit_ratio=strat1.data['Hit Ratio'][0]
strat1_win_pct=strat1.data['Win Pct'][0]
strat1_loss_pct=strat1.data['Loss Pct'][0]

#printing our strat1 metrics
print('Strat 1 Hit Ratio:',strat1_hit_ratio)
print('Strat 1 Win Percentage:',strat1_win_pct)
print('Strat 1 Loss Percentage:',strat1_loss_pct)
print('Strat 1 Total Trades:',strat1_trades)

