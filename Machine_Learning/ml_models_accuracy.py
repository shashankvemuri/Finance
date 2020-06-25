import pandas as pd
import numpy as np
from pandas_datareader import DataReader
import datetime
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt 
from sklearn.linear_model import LinearRegression 
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from pylab import rcParams

#pd.set_option("display.max_columns", None)
#pd.set_option("display.max_rows", 50)


stock = "AAPL"
start_date = datetime.datetime.now() - datetime.timedelta(days=365)
end_date = datetime.date.today()

df = DataReader(stock, "yahoo", start_date, end_date)

rows = df.values.tolist() 

forecast_out = 30 
df['Prediction'] = df[['Close']].shift(-forecast_out)

X = np.array(df.drop(['Prediction'],1))

X = X[:-forecast_out]

y = np.array(df['Prediction'])
Y = y[:-forecast_out]


x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2) # split training and test data


# Convert lists into numpy arrays 
x_train = np.array(x_train)
y_train = np.array(y_train)
x_test = np.array(x_test)
y_test = np.array(y_test)

# reshape the values as we have only one input feature
#x_train = x_train.reshape(-1,1)
#x_test = x_test.reshape(-1,1)

# Linear Regression model
clf_lr = LinearRegression()
clf_lr.fit(x_train,y_train)
y_pred_lr = clf_lr.predict(x_test)

# Support Vector Machine with a Radial Basis Function as kernel 
clf_svr = SVR(kernel="rbf", C=1e3, gamma=0.1)
clf_svr.fit(x_train,y_train)
y_pred_svr = clf_svr.predict(x_test)

# Random Forest Regressor
clf_rf = RandomForestRegressor(n_estimators=100)
clf_rf.fit(x_train,y_train)
y_pred_rf = clf_rf.predict(x_test)

# Gradient Boosting Regressor
clf_gb = GradientBoostingRegressor(n_estimators=200)
clf_gb.fit(x_train,y_train)
y_pred_gb = clf_gb.predict(x_test)


x_forecast = np.array(df.drop(['Prediction'],1))[-forecast_out:]

lr_prediction = clf_lr.predict(x_forecast)
svm_prediction = clf_svr.predict(x_forecast)
rfg_prediction = clf_rf.predict(x_forecast)
gbr_prediction = clf_gb.predict(x_forecast)

lr_confidence = round(clf_lr.score(x_test,y_test), 2)
svm_confidence = round(clf_svr.score(x_test,y_test), 2)
rfg_confidence = round(clf_rf.score(x_test,y_test), 2)
gbr_confidence = round(clf_gb.score(x_test,y_test), 2)


plt.plot(svm_prediction, markerfacecolor='orange', label = "lr confidence: {}".format(lr_confidence)) #, marker = 'o')
plt.plot(lr_prediction, markerfacecolor='blue', label = "svm confidence: {} ".format(svm_confidence)) #, marker = 'o')
plt.plot(rfg_prediction, markerfacecolor='red', label = "rfg confidence: {}".format(rfg_confidence)) #, marker = 'o')
plt.plot(gbr_prediction, markerfacecolor='green', label = "gbr confidence: {} ".format(gbr_confidence)) #, marker = 'o')
plt.legend(loc=10)
plt.title(stock)
rcParams['figure.figsize'] = 15, 10
plt.grid(True)
plt.xticks(np.arange(0, 30, step=1))
plt.xlabel('Days')
plt.ylabel('Close Price')
#plt.subplots.axis('scaled')
plt.tight_layout()
plt.show()

print("Accuracy of Linear Regression Model: ", lr_confidence)
print("Accuracy of SVM-RBF Model: ", svm_confidence)
print("Accuracy of Random Forest Model: ", rfg_confidence)
print("Accuracy of Gradient Boosting Model: ", gbr_confidence)


'''
f,(ax1, ax2) = plt.subplots(1,2,figsize=(30,10))

# Linear Regression
ax1.scatter(range(len(y_test)),y_test,label="data")
ax1.plot(range(len(y_test)),y_pred_lr,color="green",label="LR model")
ax1.legend()

# Support Vector Machine
ax2.scatter(range(len(y_test)),y_test,label="data")
ax2.plot(range(len(y_test)),y_pred_svr,color="orange",label="SVM-RBF model")
ax2.legend()

f,(ax3,ax4) = plt.subplots(1,2, figsize=(30,10))

# Random Forest Regressor
ax3.scatter(range(len(y_test)),y_test,label="data")
ax3.plot(range(len(y_test)),y_pred_rf,color="red",label="RF model")
ax3.legend()

# Gradient Boosting Regressor
ax4.scatter(range(len(y_test)),y_test,label="data")
ax4.plot(range(len(y_test)),y_pred_gb,color="black",label="GB model")
ax4.legend()
'''