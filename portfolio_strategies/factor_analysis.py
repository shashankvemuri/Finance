import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import seaborn as sns
import yfinance as yf
from factor_analyzer import FactorAnalyzer, calculate_bartlett_sphericity, calculate_kmo

# Setting plot aesthetics
sns.set(style='darkgrid', context='talk', palette='Dark2')

# Defining the time frame for data collection
end_date = dt.datetime.now()
start_date = end_date - dt.timedelta(days=365 * 7)

# List of stock symbols for factor analysis
symbols = ['AAPL', 'MSFT', 'AMD', 'NVDA']

# Fetching adjusted close prices for the specified symbols
df = pd.DataFrame({symbol: yf.download(symbol, start_date, end_date)['Adj Close']
                   for symbol in symbols})

# Initializing FactorAnalyzer and fitting it to our data
fa = FactorAnalyzer(rotation=None, n_factors=df.shape[1])
fa.fit(df.dropna())

# Extracting communalities, eigenvalues, and factor loadings
communalities = fa.get_communalities()
eigenvalues, _ = fa.get_eigenvalues()
loadings = fa.loadings_

# Plotting the Scree plot to assess the number of factors
plt.figure(figsize=(10, 6))
plt.scatter(range(1, df.shape[1] + 1), eigenvalues)
plt.plot(range(1, df.shape[1] + 1), eigenvalues)
plt.title('Scree Plot')
plt.xlabel('Number of Factors')
plt.ylabel('Eigenvalue')
plt.grid(True)
plt.show()

# Bartlett's test of sphericity
chi_square_value, p_value = calculate_bartlett_sphericity(df.dropna())
print('Bartlett sphericity test:\nChi-square value:', chi_square_value, '\nP-value:', p_value)

# Kaiser-Meyer-Olkin (KMO) test
kmo_all, kmo_model = calculate_kmo(df.dropna())
print('Kaiser-Meyer-Olkin (KMO) Test:\nOverall KMO:', kmo_all, '\nKMO per variable:', kmo_model)

# Printing results
print("\nFactor Analysis Results:")
print("\nCommunalities:\n", communalities)
print("\nFactor Loadings:\n", loadings)