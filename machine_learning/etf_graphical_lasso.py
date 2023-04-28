# Import dependencies
import pandas as pd
import numpy as np
from pandas_datareader import data as pdr
import yfinance
import datetime as dt
from sklearn import covariance
import seaborn as sns
import matplotlib.pyplot as plt
import networkx as nx
from pylab import rcParams

# Use yfinance as the default data source
yfinance.pdr_override()

# Set the number of years to retrieve the data
num_of_years = 10

# Calculate the start and end dates
start = dt.datetime.now() - dt.timedelta(int(365.25 * num_of_years))
end = dt.datetime.now()

# Define a mapping from ticker to country
etfs = {"EWJ": "Japan",
        "EWZ": "Brazil",
        "FXI": "China",
        "EWY": "South Korea",
        "EWT": "Taiwan",
        "EWH": "Hong Kong",
        "EWC": "Canada",
        "EWG": "Germany",
        "EWU": "United Kingdom",
        "EWA": "Australia",
        "EWW": "Mexico",
        "EWL": "Switzerland",
        "EWP": "Spain",
        "EWQ": "France",
        "EIDO": "Indonesia",
        "ERUS": "Russia",
        "EWS": "Singapore",
        "EWM": "Malaysia",
        "EZA": "South Africa",
        "THD": "Thailand",
        "ECH": "Chile",
        "EWI": "Italy",
        "TUR": "Turkey",
        "EPOL": "Poland",
        "EPHE": "Philippines",
        "EWD": "Sweden",
        "EWN": "Netherlands",
        "EPU": "Peru",
        "ENZL": "New Zealand",
        "EIS": "Israel",
        "EWO": "Austria",
        "EIRL": "Ireland",
        "EWK": "Belgium"}

# Separate the keys and values from the mapping dictionary
symbols, names = np.array(sorted(etfs.items())).T

# Load the data from input.csv into a pandas DataFrame
df = pdr.get_data_yahoo(symbols.tolist(), start, end)['Adj Close']

# Convert price series to log return series
df = np.log1p(df.pct_change()).iloc[1:]

# Fit the Glasso algorithm to the data to calculate the precision matrix
edge_model = covariance.GraphicalLassoCV(cv=10)
df /= df.std(axis=0)
df = df.dropna()
edge_model.fit(df)
p = edge_model.precision_

# Plot the heatmap of the precision matrix
rcParams['figure.figsize'] = 15, 10
sns.heatmap(p)
plt.show()

# Prepare the matrix for network illustration
p = pd.DataFrame(p)
links = p.stack().reset_index()
links.columns = ['var1', 'var2', 'value']

# Filter the links to only include those with absolute value greater than 0.17
# and exclude those with var1 equal to var2
links = links.loc[(abs(links['value']) > 0.17) & (links['var1'] != links['var2'])]

# Build the graph using networkx library
G = nx.from_pandas_edgelist(links, 'var1', 'var2', create_using=nx.Graph())
pos = nx.spring_layout(G, k=0.2 * 1 / np.sqrt(len(G.nodes())), iterations=20)
plt.figure(3, figsize=(15, 15))
nx.draw(G, pos=pos)
nx.draw_networkx_labels(G, pos=pos)
plt.show()

# Write to graph.gexf
nx.write_gexf(G, 'graph.gexf')