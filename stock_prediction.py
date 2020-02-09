#Install the dependencies
import numpy as np 
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import pandas_datareader.data as web
import datetime
from pylab import rcParams

# Import data
s = 'NIO'
start_date = datetime.datetime(2019,1,1)
end_date = datetime.date.today()

# Get the stock data
df = web.DataReader(s, 'yahoo', start_date, end_date)
df = df[['Close']] 
# Take a look at the data
print ("These are the Close Prices for the past 5 days")
print(df.tail())



# A variable for predicting 'n' days out into the future
forecast_out = 30 #'n=30' days
#Create another column (the target ) shifted 'n' units up
df['Prediction'] = df[['Close']].shift(-forecast_out)
#print the new data set
#print(df.tail())


### Create the independent data set (X)  #######
# Convert the dataframe to a numpy array
X = np.array(df.drop(['Prediction'],1))


#Remove the last '30' rows
X = X[:-forecast_out]
#print(X)


### Create the dependent data set (y)  #####
# Convert the dataframe to a numpy array 
y = np.array(df['Prediction'])
# Get all of the y values except the last '30' rows
y = y[:-forecast_out]
#print(y)


# Split the data into 80% training and 20% testing
x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2)


# Create and train the Support Vector Machine (Regressor) 
svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1) 
svr_rbf.fit(x_train, y_train)


# Testing Model: Score returns the coefficient of determination R^2 of the prediction. 
# The best possible score is 1.0
svm_confidence = svr_rbf.score(x_test, y_test)
print("svm confidence: ", svm_confidence)


# Create and train the Linear Regression  Model
lr = LinearRegression()
# Train the model
lr.fit(x_train, y_train)


# Testing Model: Score returns the coefficient of determination R^2 of the prediction. 
# The best possible score is 1.0
lr_confidence = lr.score(x_test, y_test)
print("lr confidence: ", lr_confidence)


# Set x_forecast equal to the last 30 rows of the original data set from Adj. Close column
x_forecast = np.array(df.drop(['Prediction'],1))[-forecast_out:]
#print(x_forecast)


# Print linear regression model predictions for the next '30' days
lr_prediction = lr.predict(x_forecast)
#print(lr_prediction)

# Print support vector regressor model predictions for the next '30' days
svm_prediction = svr_rbf.predict(x_forecast)
#print(svm_prediction)

plt.plot(svm_prediction, markerfacecolor='orange', label = "svm regressor: {}".format(svm_confidence)) #, marker = 'o')
plt.plot(lr_prediction, markerfacecolor='blue', label = "lr confidence: {} ".format(lr_confidence)) #, marker = 'o')
plt.legend(loc=10)
plt.title(s)
rcParams['figure.figsize'] = 15, 10
txt = "lr confidence: ", lr_confidence 
txt1 = "svm confidence: ", svm_confidence
plt.grid(True)
plt.xticks(np.arange(0, 30, step=1))
plt.xlabel('Days')
plt.ylabel('Close Price')
#plt.subplots.axis('scaled')
plt.tight_layout()
plt.show()