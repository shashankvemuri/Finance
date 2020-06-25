#import packages for use later in the HMM code
import pandas as pd
import sklearn.mixture as mix
import numpy as np
import datetime as dt
from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib.dates import YearLocator, MonthLocator
import seaborn as sns
from pandas_datareader import DataReader
from sklearn.model_selection import train_test_split

ticker = "AAPL"

# Change these if needed
start_date = dt.datetime.now() - dt.timedelta(days=365*5)
end_date = dt.date.today()

for t in ticker:
    df = DataReader(t, 'yahoo', start_date, end_date)

    df["Return"] = df["Close"].pct_change()
    
    df["Range"] = (df["High"]/df["Low"])-1
    
    del df["High"]
    del df["Low"]
    
    df.dropna(how="any", inplace=True)

print(df)

#create train and test sets
#this methodology will randomly select 80% of our data
msk = np.random.rand(len(df)) < 0.8
train = df[msk]
test = df[~msk]

print (train)
print (test)

X_train = train[["Return", "Range", "Close"]]
X_test = test[["Return", "Range", "Close"]]

model = mix.GaussianMixture(n_components=3, covariance_type="full", n_init=100, random_state=7).fit(X_train)

# Predict the optimal sequence of internal hidden state
hidden_states = model.predict(X_test)

print("Means and vars of each hidden state")
for i in range(model.n_components):
    print("{0}th hidden state".format(i))
    print("mean = ", model.means_[i])
    print("var = ", np.diag(model.covariances_[i]))
    print()

sns.set(font_scale=1.25)
style_kwds = {'xtick.major.size': 3, 'ytick.major.size': 3,
              'font.family':u'DejaVu Sans ', 'legend.frameon': True}
sns.set_style('white', style_kwds)

fig, axs = plt.subplots(model.n_components, sharex=True, sharey=True, figsize=(12,9))
colors = cm.rainbow(np.linspace(0, 1, model.n_components))

for i, (ax, color) in enumerate(zip(axs, colors)):
    # Use fancy indexing to plot data in each state.
    mask = hidden_states == i
    ax.plot_date(X_test.index.values[mask],
                 X_test["Close"].values[mask],
                 ".-", c=color)
    ax.set_title("{0}th hidden state".format(i), fontsize=16, fontweight='demi')

    # Format the ticks.
    ax.xaxis.set_major_locator(YearLocator())
    ax.xaxis.set_minor_locator(MonthLocator())
    sns.despine(offset=10)

plt.tight_layout()

sns.set(font_scale=1.5)
states = (pd.DataFrame(hidden_states, columns=['states'], index=X_test.index)
          .join(X_test, how='inner')
          .reset_index(drop=False)
          .rename(columns={'index':'Date'}))
states.head()

#suppressing warnings because of some issues with the font package
#in general, would not rec turning off warnings.
import warnings
warnings.filterwarnings("ignore")

sns.set_style('white', style_kwds)
order = [0, 1, 2]
fg = sns.FacetGrid(data=states, hue='states', hue_order=order,
                   palette=colors, aspect=1.31, height=12)
fg.map(plt.scatter, 'Date', "Close", alpha=0.8).add_legend()
sns.despine(offset=10)
fg.fig.suptitle('Historical {} Regimes'.format(ticker), fontsize=24, fontweight='demi')

