import io
import math
import numpy
import pydotplus
import numpy as np
import pandas as pd
import datetime as dt
from sklearn import tree
from sklearn import metrics
from sklearn.svm import SVC
from google.colab import files
import matplotlib.pyplot as plt
from IPython.display import Image
import pandas_datareader.data as web
from sklearn.metrics import accuracy_score
from sklearn.externals.six import StringIO
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

uploaded = files.upload()

df = pd.read_csv(io.BytesIO(uploaded['EA_sports_tweets_cleaned.csv']))
df = df[['Date','Tweet content','Followers']]

def sentimentScore(Tweet):
    analyzer = SentimentIntensityAnalyzer()
    score_values = []
    for tweet in df['Tweet content']:
        vs1 = analyzer.polarity_scores(tweet)
        print("Score: " + str(vs1))
        score_values.append(vs1)
    return score_values

sentiment_scores = pd.DataFrame(sentimentScore(df['Tweet content']))

raw_ads = pd.merge(df, sentiment_scores, left_index=True, right_index=True)
raw_ads = raw_ads[(raw_ads['Date'] >= '2016-04-01') & (raw_ads['Date'] <= '2016-06-14')]

raw_ads['datetime'] = pd.to_datetime(raw_ads['Date'])

raw_ads_2 = raw_ads[(raw_ads['compound'] !=0)]

raw_ads_3 = raw_ads_2[raw_ads_2['Followers'].isnull()==False]

raw_ads_3['sentiment_score'] = raw_ads_3['compound']*raw_ads_3['Followers']

raw_ads_3.reset_index()

raw_ads_4=(raw_ads_3.groupby(raw_ads_3.Date).mean())

ticker = input("Enter ticker")

initial_date = dt.datetime(2016, 4, 2)
final_date =  dt.datetime(2016, 6, 14)

stock_data = web.DataReader(ticker, 'yahoo', initial_date, final_date)

stock_data.columns = ['High','Low','Open','Close','Volume_of_stock','Adj_Close_stock']

stock_data['stock_val_change'] = (stock_data['Close'] - stock_data['Open']) / stock_data['Open'] * 100.0

scaler = StandardScaler()
stock_data['stock_val_change_scaled'] = scaler.fit_transform(stock_data[['stock_val_change']])

dataset = pd.merge(stock_data[['Open', 'Volume_of_stock','Adj_Close_stock','stock_val_change', 'stock_val_change_scaled']], raw_ads_4[['sentiment_score']], left_index=True, right_index=True)

forecast_col = 'stock_val_change'
forecast_out = int(math.ceil(0.013 * len(dataset)))
dataset['stock_val_change_pred'] = dataset[forecast_col].shift(-forecast_out)

dataset['buy_sell'] = dataset['stock_val_change_pred'].apply(lambda x: 1 if x >=0 else -1)
train_set = dataset.iloc[:35]
test_set = dataset.iloc[35:]

X_train = np.array(train_set[['sentiment_score']])
X_test = np.array(test_set[['sentiment_score']])

y_train = np.array(train_set['buy_sell'])
y_test = np.array(test_set['buy_sell'])

scaler = StandardScaler()
X_train_std= scaler.fit_transform(X_train)

for i in range(1,5):
    knn = KNeighborsClassifier(n_neighbors=i).fit(X_train_std, y_train)
    y_test_pred = knn.predict(X_test)
    print(accuracy_score(y_test, y_test_pred))

knn = KNeighborsClassifier(n_neighbors=3).fit(X_train, y_train)
y_test_pred = knn.predict(X_test)

knn_list =[]
knn_list.append(y_test_pred)

for i in range(1,5):
    svc= SVC(kernel="linear", random_state=0, gamma=i)
    model= svc.fit(X_train_std, y_train)
    scores = cross_val_score(estimator=model, X=X_train_std, y=y_train, cv=5)
    print(i, ':', np.average(scores))

for i in range(1,5):
    svc= SVC(kernel="rbf", random_state=0, gamma=i)
    model= svc.fit(X_train_std, y_train)
    scores = cross_val_score(estimator=model, X=X_train, y=y_train, cv=5)
    print(i, ':', np.average(scores))

for i in range(1,5):
    svc= SVC(kernel="poly", random_state=0, gamma=i)
    model= svc.fit(X_train_std, y_train)
    scores = cross_val_score(estimator=model, X=X_train_std, y=y_train, cv=5)
    print(i, ':', np.average(scores))

for i in range(1,5):
    svc= SVC(kernel="sigmoid", random_state=0, gamma=i)
    model= svc.fit(X_train_std, y_train)
    scores = cross_val_score(estimator=model, X=X_train_std, y=y_train, cv=5)
    print(i, ':', np.average(scores))

svc= SVC(kernel="rbf", random_state=0, gamma=3)
model= svc.fit(X_train_std, y_train)
y_test_pred = model.predict(X_test)

svmlist =[]
svmlist.append(y_test_pred)

# Cross-validation
decisiontree= DecisionTreeClassifier(max_depth=4)
model = decisiontree.fit(X_train_std, y_train)
y_test_pred = model.predict(X_test)
accuracy_score(y_test, y_test_pred)

#Add to the list
dtlist =[]
dtlist.append(y_test_pred)

#Visualize the tree
features = ['buy_sell']

dot_data = StringIO()  
tree.export_graphviz(decisiontree, out_file=dot_data,  
                         feature_names=features)  
graph = pydotplus.graph_from_dot_data(dot_data.getvalue())  
Image(graph.create_png())

randomforest = RandomForestClassifier(random_state=5, bootstrap=0, n_estimators=1000)

model=randomforest.fit(X_train_std, y_train)
y_test_pred = model.predict(X_test)
accuracy_score(y_test, y_test_pred)

#Add to the list
rflist = []
rflist.append(y_test_pred)

lr=LogisticRegression()
model = lr.fit(X_train_std, y_train)

# Calculate the accuracy score
y_test_pred = lr.predict(X_test)
print(metrics.accuracy_score(y_test,y_test_pred))

#Add to te list
lrlist=[]
lrlist.append(y_test_pred)

#Finding the parameters to build the best net
for i in range(2,21):
    model4= MLPClassifier(hidden_layer_sizes=(i),max_iter=1000)
    scores= cross_val_score(estimator= model4, X=X_train_std, y=y_train, cv=5)
    print(i, '-', numpy.average(scores))

#Add to te list
mlp = MLPClassifier(hidden_layer_sizes=(2), max_iter=1000)
model = mlp.fit(X_train_std, y_train)
y_test_pred = model.predict(X_test)

annlist=[]
annlist.append(y_test_pred)

outcome_df = pd.DataFrame({'Regular': y_test, 'KNN': knn_list[0], 'SVM': svmlist[0], 'Decision_Tree': dtlist[0], 'Random_Forest': rflist[0], 'Logistic': lrlist[0], 'ANN': annlist[0]})

predictions = pd.merge(dataset.iloc[35:].reset_index(), outcome_df, left_index=True, right_index = True)

predictions.head(2)

predictions["Gain_or_Loss_KNN"] = (predictions['Adj_Close_stock'] - predictions['Open'])*predictions['KNN']
predictions["Gain_or_Loss_SVM"] = (predictions['Adj_Close_stock'] - predictions['Open'])*predictions['SVM']
predictions["Gain_or_Loss_DecisionTree"] = (predictions['Adj_Close_stock'] - predictions['Open'])*predictions['Decision_Tree']
predictions["Gain_or_Loss_Random_Forest"] = (predictions['Adj_Close_stock'] - predictions['Open'])*predictions['Random_Forest']
predictions["Gain_or_Loss_Logistic"] = (predictions['Adj_Close_stock'] - predictions['Open'])*predictions['Logistic']
predictions["Gain_or_Loss_ANN"] = (predictions['Adj_Close_stock'] - predictions['Open'])*predictions['ANN']

predictions.head()

first_day_result = predictions.iloc[0]['Adj_Close_stock']
predictions.at[ 0, 'KNN_Result']= first_day_result
predictions.at[ 0, 'LogReg_Result']= first_day_result
predictions.at[ 0, 'SVM_Result']= first_day_result
predictions.at[ 0, 'Naive_Bayes_Result']= first_day_result
predictions.at[ 0, 'Decision_Tree_Result']= first_day_result
predictions.at[ 0, 'Random_Forest_Result']= first_day_result
predictions.at[ 0, 'ANN_Result']= first_day_result

for i in range(1, len(predictions)):
    predictions.loc[i, 'KNN_Result'] = predictions.loc[i-1, 'KNN_Result'] + predictions.loc[i, 'Gain_or_Loss_KNN']
    predictions.loc[i, 'LogReg_Result'] = predictions.loc[i-1, 'LogReg_Result'] + predictions.loc[i, 'Gain_or_Loss_Logistic']
    predictions.loc[i, 'SVM_Result'] = predictions.loc[i-1, 'SVM_Result'] + predictions.loc[i, 'Gain_or_Loss_SVM']
    predictions.loc[i, 'Decision_Tree_Result'] = predictions.loc[i-1, 'Decision_Tree_Result'] + predictions.loc[i, 'Gain_or_Loss_DecisionTree']
    predictions.loc[i, 'Random_Forest_Result'] = predictions.loc[i-1, 'Random_Forest_Result'] + predictions.loc[i, 'Gain_or_Loss_Random_Forest']
    predictions.loc[i, 'ANN_Result'] = predictions.loc[i-1, 'ANN_Result'] + predictions.loc[i, 'Gain_or_Loss_ANN']

plt.style.use('fivethirtyeight') 
plt.rcParams['figure.figsize'] = 25, 22 
plt.suptitle('Electronic Arts (EA) 28.2.-28.3.2019', fontsize=30)

ax1 = predictions['Adj_Close_stock']
ax2 = predictions['KNN_Result']
ax3 = predictions['LogReg_Result']
ax4 = predictions['SVM_Result']
ax5 = predictions['Decision_Tree_Result']
ax6 = predictions['Random_Forest_Result']
ax7 = predictions['ANN_Result']

for i in range (1, 7):
    plt.subplots_adjust(hspace=0.6, wspace=0.15)
        
    plt.subplot(3,2,1)
    plt.plot(ax1, 'r',  linewidth=2)
    plt.plot(ax2,  'b',  linestyle=':', linewidth=5)
    plt.xlabel('Days', fontsize=20)
    plt.ylabel('Price', fontsize=20)
    plt.title('KNN',  fontsize=25)
    a='Buy-and-hold'
    b='KNN'
    plt.legend((a,b), fontsize=20, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=True)
    
    plt.subplot(3,2,2)
    plt.plot(ax1, 'r',  linewidth=2 )
    plt.plot(ax3, 'g',  linestyle=':', linewidth=5)
    plt.xlabel('Days', fontsize=20)
    plt.ylabel('Price', fontsize=20)
    plt.title('Logistic Regression', fontsize=25)
    a='Buy-and-hold'
    b='Log Reg'
    plt.legend((a,b), fontsize=20, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=True)
    
    plt.subplot(3,2,3)
    plt.plot(ax1, 'r',  linewidth=2 )
    plt.plot(ax4, 'c',  linestyle=':', linewidth=5)
    plt.xlabel('Days', fontsize=20)
    plt.ylabel('Price', fontsize=20)
    plt.title('SVM', fontsize=25)
    a='Buy-and-hold'
    b='SVM'
    plt.legend((a,b), fontsize=20, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=True)
    
    plt.subplot(3,2,4)
    plt.plot(ax1, 'r',  linewidth=2 )
    plt.plot(ax5, 'm',  linestyle=':', linewidth=5)
    plt.xlabel('Days', fontsize=20)
    plt.ylabel('Price', fontsize=20)
    plt.title('Decision Tree', fontsize=25)
    a='Buy-and-hold'
    b='Decision Tree'
    plt.legend((a,b), fontsize=20, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=True)
    
    plt.subplot(3,2,5)
    plt.plot(ax1, 'r',  linewidth=2 )
    plt.plot(ax6, 'royalblue',  linestyle=':', linewidth=5)
    plt.xlabel('Days', fontsize=20)
    plt.ylabel('Price', fontsize=20)
    plt.title('Random Forest', fontsize=25)
    a='Buy-and-hold'
    b='Random Forest'
    plt.legend((a,b), fontsize=20, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=True)
    
    plt.subplot(3,2,6)
    plt.plot(ax1, 'r',  linewidth=2 )
    plt.plot(ax7, 'saddlebrown',  linestyle=':', linewidth=5)
    plt.xlabel('Days', fontsize=20)
    plt.ylabel('Price', fontsize=20)
    plt.title('Artificial Neural Network', fontsize=25)
    a='Buy-and-hold'
    b='ANN'
    plt.legend((a,b), fontsize=20, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=True)

plt.show()
