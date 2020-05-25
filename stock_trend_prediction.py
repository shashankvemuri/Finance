import time
import talib
import datetime
import numpy as np
import pandas as pd
from sklearn.svm import SVC
import matplotlib.pyplot as plt
from pandas_datareader import DataReader
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import MinMaxScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

start_date = datetime.datetime(1969, 1, 1)
end_date = datetime.date.today()

df = DataReader('^DJI', 'yahoo', start_date, end_date)

print(df.head())
print ('\n')
print(df.shape)
print ('\n')
print(df.columns)
print ('\n')
print(df.index)
print ('\n')

#plot closing price for DJI
df.Close.plot(grid=True, figsize=(10,6));
plt.title("DJI Closing price")

#Create technical indicators
ti = pd.DataFrame(index=df.index)

# open, high, low, close, volume
ti["Open"] = df["Open"]
ti["High"] = df["High"]
ti["Low"] = df["Low"]
ti["Close"] = df["Close"]
ti["Volume"] = df["Volume"]

# Simple Moving Average
ti["SMA_10"] = (sum(ti.Close, 10))/10
ti["SMA_20"] = (sum(ti.Close, 20))/20
ti["SMA_50"] = (sum(ti.Close, 50))/50
ti["SMA_100"] = (sum(ti.Close, 100))/100
ti["SMA_200"] = (sum(ti.Close, 200))/200

# Exponential Moving Average
ti["EMA_10"] = ti.Close.ewm(span=10).mean().fillna(0)
ti["EMA_20"] = ti.Close.ewm(span=20).mean().fillna(0)
ti["EMA_50"] = ti.Close.ewm(span=50).mean().fillna(0)
ti["EMA_100"] = ti.Close.ewm(span=100).mean().fillna(0)
ti["EMA_200"] = ti.Close.ewm(span=200).mean().fillna(0) 

# Average True Range
ti["ATR"] = talib.ATR(ti.High, ti.Low, ti.Close, timeperiod=14)

# Average Directional Index
ti["ADX"] = talib.ADX(ti.High, ti.Low, ti.Close, timeperiod=14)

# Commodity Channel Index
#ti["CCI"] = talib.CCI(ti.High, ti.Low, ti.Close, timeperiod=20)
tp = (ti["High"] + ti["Low"] + ti["Close"]) / 3
ma = tp / 20
md = (tp - ma) / 20
ti["CCI"] = (tp - ma)/(0.015*md)

# Price rate-of-change
#ti["ROC"] = talib.ROC(ti.Close)
ti["ROC"] = ((ti["Close"] - ti["Close"].shift(12))/(ti["Close"].shift(12)))*100

# Relative Strength Index
ti["RSI"] = talib.RSI(ti.Close, timeperiod=14)

# William’s %R
ti["William’s %R"] = talib.WILLR(ti.High, ti.Low, ti.Close, timeperiod=14)

# Stochastic %K
ti["SO%K"] = (ti.Close - ti.Low)/(ti.High - ti.Low)

ti.dropna(inplace=True)

ti["pred_price"] = np.where(ti.Close.shift(-1) > ti.Close, 1, 0)

ti.head()

# spit data into features and target variable
x = ti.drop(columns=["pred_price"])
y = ti.pred_price

# split data in training and testing sets
train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=0.3, shuffle=False)

print(f"Observations: {len(x)}")
print ('\n')
print(f"Train Dataset: {train_x.shape}")
print ('\n')
print(f"Test Dataset: {test_x.shape}")
print ('\n')

# plot training and testing data
ax = train_x.plot(grid=True, figsize=(10, 6))
test_x.plot(ax=ax, grid=True)
plt.title('DOW Jones Industrial Average Volatility')
plt.legend(["train", "test"])

# normalize data
scaler = MinMaxScaler(feature_range=(0,1))

train_x_scaled = scaler.fit_transform(train_x)
test_x_scaled = scaler.transform(test_x)

# 4 Train classification models

dict_classifiers = {
    "Logistic Regression": LogisticRegression(solver="lbfgs", max_iter=5000),
    "Nearest Neighbors": KNeighborsClassifier(),
    "Support Vector Machine": SVC(gamma = "auto"),
    "Decision Tree": DecisionTreeClassifier(),
    "Random Forest": RandomForestClassifier(n_estimators=100),
    "Neural Net": MLPClassifier(solver="adam", alpha=0.0001, learning_rate="constant", learning_rate_init=0.001),
    "Naive Bayes": GaussianNB()
}

no_classifiers = len(dict_classifiers.keys())

def batch_classify(train_x_scaled, train_y, verbose=True):
  df_results = pd.DataFrame(data=np.zeros(shape=(no_classifiers, 3)), 
                            columns=["classifier", "train_score", "training_time"])
  count = 0
  for key, classifier in dict_classifiers.items():
    t_start = time.process_time()
    classifier.fit(train_x_scaled, train_y)
    t_end = time.process_time()
    t_diff = t_end - t_start
    train_score = classifier.score(train_x_scaled, train_y)
    df_results.loc[count, "classifier"] = key
    df_results.loc[count, "train_score"] = train_score
    df_results.loc[count, "training_time"] = t_diff
    if verbose:
      print(f"Trained {key} in {t_diff:.3f}s")
    count += 1
  return df_results

df_results = batch_classify(train_x_scaled, train_y)
print(df_results.sort_values(by="train_score", ascending=True))
print ('\n')

# 5 Make prediction
classifier = LogisticRegression(solver='lbfgs', max_iter=5000)
classifier.fit(train_x_scaled, train_y)

predictions = classifier.predict(test_x_scaled)
print(f"accuracy score: {accuracy_score(test_y, predictions)}")
print ('\n')
print(f"confusion matric:")
print(confusion_matrix(test_y, predictions))
print ('\n')
print(f"classification report:")
print(classification_report(test_y, predictions))

# Check target variables
check_df = pd.DataFrame()
check_df["Close"] = test_x["Close"]
check_df["pred_price"] = test_y

print ('\n')
print(check_df)