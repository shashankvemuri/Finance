import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import seaborn as sns
import math
import yfinance as yf
from dateutil import relativedelta
from factor_analyzer import FactorAnalyzer, calculate_bartlett_sphericity, calculate_kmo, ConfirmatoryFactorAnalyzer, ModelSpecificationParser

# Set the start and end dates for downloading data
end = dt.datetime.now()
start = end - dt.timedelta(days=365 * 7)

# Define the symbols to download
symbols = ['AAPL', 'MSFT', 'AMD', 'NVDA']

# Download the data using yfinance
df = pd.DataFrame()
for symbol in symbols:
    df[symbol] = yf.download(symbol, start, end)['Adj Close']

# Perform factor analysis using the downloaded data
fa = FactorAnalyzer(rotation=None)
fa.fit(df)

# Print the communalities of each variable
print(fa.get_communalities())

# Get the eigenvalues of the factors
ev, v = fa.get_eigenvalues()

# Plot the scree plot to determine the number of factors
plt.scatter(range(1, df.shape[1]+1), ev)
plt.plot(range(1, df.shape[1]+1), ev)
plt.title('Scree Plot')
plt.xlabel('Factors')
plt.ylabel('Eigenvalue')
plt.grid()
plt.show()

# Calculate the Bartlett's test of sphericity
chi_square_value, p_value = calculate_bartlett_sphericity(df)
print('Bartlett sphericity test:')
print('Chi-square value:', chi_square_value)
print('P-value:', p_value)

# Calculate the Kaiser-Meyer-Olkin (KMO) measure of sampling adequacy
kmo_all, kmo_model = calculate_kmo(df)
print('Kaiser-Meyer-Olkin measure of sampling adequacy:')
print('Overall KMO:', kmo_all)
print('KMO for each variable:', kmo_model)

# Fit the confirmatory factor analysis model and print the loadings and factor covariance matrix
model_spec = ModelSpecificationParser.parse_model_specification_from_dict(df)
cfa = ConfirmatoryFactorAnalyzer(model_spec, disp=False)
cfa.fit(df.values)
print('Loadings:')
print(cfa.loadings_)
print('Factor covariance matrix:')
print(cfa.factor_varcovs_)

# Transform the data using the fitted model
cfa.transform(df.values)