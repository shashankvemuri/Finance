# Import necessary libraries
import pandas as pd
import numpy as np
import datetime
from pandas_datareader import DataReader
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import matplotlib.pyplot as plt
from pylab import rcParams

# Define the stock and date range for analysis
stock = "AAPL"
start_date = datetime.datetime.now() - datetime.timedelta(days=365)
end_date = datetime.date.today()

# Fetch stock data
df = DataReader(stock, "yahoo", start_date, end_date)

# Prepare the dataset for prediction
forecast_out = 30
df['Prediction'] = df[['Close']].shift(-forecast_out)
X = np.array(df.drop(['Prediction'], 1))[:-forecast_out]
y = np.array(df['Prediction'])[:-forecast_out]

# Split data into training and testing sets
x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Define and train multiple machine learning models
models = {
    "Linear Regression": LinearRegression(),
    "SVR": SVR(kernel="rbf", C=1e3, gamma=0.1),
    "Random Forest": RandomForestRegressor(n_estimators=100),
    "Gradient Boosting": GradientBoostingRegressor(n_estimators=200)
}
predictions = {}
for name, model in models.items():
    model.fit(x_train, y_train)
    predictions[name] = model.predict(x_test)

# Predict future values
x_forecast = np.array(df.drop(['Prediction'], 1))[-forecast_out:]
future_predictions = {name: model.predict(x_forecast) for name, model in models.items()}

# Compute and display model accuracies
accuracies = {name: model.score(x_test, y_test) for name, model in models.items()}
for name, accuracy in accuracies.items():
    print(f"Accuracy of {name}: {accuracy:.2f}")

# Plot the predictions
plt.figure(figsize=(15, 10))
for name, preds in future_predictions.items():
    plt.plot(preds, label=f"{name} ({accuracies[name]:.2f})")
plt.legend(loc="upper left")
plt.title(f"Future Predictions by ML Models for {stock}")
plt.xlabel("Days")
plt.ylabel("Predicted Close Price")
plt.grid(True)
plt.show()

# Plot each ML model's performance on test data
fig, axs = plt.subplots(2, 2, figsize=(15, 10))
for ax, (name, preds) in zip(axs.flatten(), predictions.items()):
    ax.scatter(range(len(y_test)), y_test, label="Data", color='gray')
    ax.plot(range(len(y_test)), preds, label=f"{name}", color='orange')
    ax.set_title(f"{name} Model")
    ax.legend()
plt.tight_layout()
plt.show()