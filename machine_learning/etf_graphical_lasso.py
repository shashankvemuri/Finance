# Import necessary libraries
import pandas as pd
import numpy as np
import datetime as dt
from pandas_datareader import data as pdr
import yfinance as yf
from sklearn.covariance import GraphicalLassoCV
import seaborn as sns
import matplotlib.pyplot as plt
import networkx as nx
from pylab import rcParams

# Override pandas_datareader with yfinance
yf.pdr_override()

# Set parameters for data retrieval
num_years = 10
start_date = dt.datetime.now() - dt.timedelta(days=num_years * 365.25)
end_date = dt.datetime.now()

# ETF symbols and their respective countries
etfs = {"EWJ": "Japan", "EWZ": "Brazil", "FXI": "China",
        "EWY": "South Korea", "EWT": "Taiwan", "EWH": "Hong Kong",
        "EWC": "Canada", "EWG": "Germany", "EWU": "United Kingdom",
        "EWA": "Australia", "EWW": "Mexico", "EWL": "Switzerland",
        "EWP": "Spain", "EWQ": "France", "EIDO": "Indonesia",
        "ERUS": "Russia", "EWS": "Singapore", "EWM": "Malaysia",
        "EZA": "South Africa", "THD": "Thailand", "ECH": "Chile",
        "EWI": "Italy", "TUR": "Turkey", "EPOL": "Poland",
        "EPHE": "Philippines", "EWD": "Sweden", "EWN": "Netherlands",
        "EPU": "Peru", "ENZL": "New Zealand", "EIS": "Israel",
        "EWO": "Austria", "EIRL": "Ireland", "EWK": "Belgium"}

# Retrieve adjusted close prices for ETFs
symbols = list(etfs.keys())
etf_data = pdr.get_data_yahoo(symbols, start=start_date, end=end_date)['Adj Close']

# Convert prices to log returns
log_returns = np.log1p(etf_data.pct_change()).dropna()

# Normalize and fit Graphical Lasso model
log_returns_normalized = log_returns / log_returns.std(axis=0)
edge_model = GraphicalLassoCV(cv=10)
edge_model.fit(log_returns_normalized)

# Plot precision matrix as heatmap
rcParams['figure.figsize'] = 15, 10
sns.heatmap(edge_model.precision_, xticklabels=etfs.values(), yticklabels=etfs.values())
plt.title('Precision Matrix Heatmap')
plt.show()

# Prepare data for network graph
precision_df = pd.DataFrame(edge_model.precision_, index=etfs.keys(), columns=etfs.keys())
links = precision_df.stack().reset_index()
links.columns = ['ETF1', 'ETF2', 'Value']
links_filtered = links[(abs(links['Value']) > 0.17) & (links['ETF1'] != links['ETF2'])]

# Build and display the network graph
G = nx.from_pandas_edgelist(links_filtered, 'ETF1', 'ETF2')
pos = nx.spring_layout(G, k=0.2 * 1 / np.sqrt(len(G.nodes())), iterations=20)
plt.figure(figsize=(15, 15))
nx.draw(G, pos=pos, with_labels=True, node_color='lightblue', edge_color='grey')
plt.title('ETF Relationships Network Graph')
plt.show()

# Save network graph to file
nx.write_gexf(G, 'etf_network_graph.gexf')