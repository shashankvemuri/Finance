#cell 0
# SimFin Tutorial 07 - Stock Screener

[Original repository on GitHub](https://github.com/simfin/simfin-tutorials)

This tutorial was originally written by [Hvass Labs](https://github.com/Hvass-Labs)

----

"I am King Arthur and these are my knights of the round table. Go and tell your master that we have been charged by God with a quest for the Holy Grail and he can join us. Well I can ask him, but I don't think he'll be very keen, because he has already got one, you see."
&ndash; [Monty Python's Holy Grail](https://www.youtube.com/watch?v=M9DCAFUerzs)


#cell 1
## Introduction

A stock-screener is a very common tool used to search for stocks that meet certain criteria, e.g. low valuation ratios, high sales-growth, etc. This tutorial shows how to make a basic stock-screener using the signals calculated in the previous tutorial.

We will also show how to back-test a stock-screener to see if it would have been able to discover profitable investments in the past. And we will show how to optimize the screener criteria to maximize the average returns.

It is assumed you are already familiar with the previous tutorials on the basics of SimFin.

#cell 2
## Imports

#cell 3
%matplotlib inline
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.optimize import differential_evolution
from datetime import datetime, timedelta
import os

# Import the main functionality from the SimFin Python API.
import simfin as sf

# Import names used for easy access to SimFin's data-columns.
from simfin.names import *

#cell 4
# Version of the SimFin Python API.
sf.__version__

#cell 5
# Boolean whether this is being run under pytest. We will
# use this to make certain parts of the tutorial run faster.
running_pytest = ('PYTEST_CURRENT_TEST' in os.environ)

#cell 6
## Config

#cell 7
# SimFin data-directory.
sf.set_data_dir('~/simfin_data/')

#cell 8
# SimFin load API key or use free data.
sf.load_api_key(path='~/simfin_api_key.txt', default_key='free')

#cell 9
# Seaborn set plotting style.
sns.set_style("whitegrid")

#cell 10
## Data Hub

In these examples, we will use stock-data for USA. It is very easy to load and process the data using the `sf.StockHub` class. We instruct it to refresh the financial data every 30 days, and the share-price data must be refreshed daily.

#cell 11
hub = sf.StockHub(market='us',
                  refresh_days=30,
                  refresh_days_shareprices=1)

#cell 12
The data-hub not only makes the syntax very simple, but it also takes care of downloading the required datasets from the SimFin server and loading them into Pandas DataFrames. Furthermore, the data-hub's slow processing functions use a disk-cache to save the results for the next time the functions are called, and the cache automatically gets refreshed when new datasets are downloaded from the SimFin server. Lastly, the data-hub's functions are also RAM-cached, so the second time you call them, they return the results nearly instantly. Altogether, the data-hub makes it much easier and faster to work with the data.

#cell 13
## Financial Signals

First we calculate financial signals for the stocks, such as the Current Ratio, Debt Ratio, Net Profit Margin, Return on Assets, etc. These are calculated using data from the financial reports: Income Statements, Balance Sheets and Cash-Flow Statements, which are automatically downloaded and loaded by the data-hub.

Note that we set `variant='latest'` because we are only interested in the most recent signals, and we are not interested in the signals from several years ago.

#cell 14
%%time
df_fin_signals = hub.fin_signals(variant='latest')

#cell 15
df_fin_signals.dropna().head()

#cell 16
We then pass the argument `func=sf.avg_ttm_2y` to `hub.fin_signals`, so as to calculate 2-year averages of the financial signals. We then get another DataFrame with the 2-year average Current Ratio, Net Profit Margin, Return on Assets, etc.

#cell 17
%%time
df_fin_signals_2y = hub.fin_signals(variant='latest',
                                    func=sf.avg_ttm_2y)

#cell 18
df_fin_signals_2y.dropna().head()

#cell 19
## Growth Signals

Now we calculate growth signals for the stocks, such as Earnings Growth, FCF Growth, Sales Growth, etc. These are also calculated using data from the financial reports: Income Statements, Balance Sheets and Cash-Flow Statements, which are automatically downloaded and loaded by the data-hub.

#cell 20
%%time
df_growth_signals = hub.growth_signals(variant='latest')

#cell 21
df_growth_signals.dropna().head()

#cell 22
We then pass the argument `func=sf.avg_ttm_2y` to `hub.growth_signals` so as to calculate 2-year averages of the growth signals. We then get another DataFrame with the 2-year average Earnings Growth, FCF Growth, Sales Growth, etc.

#cell 23
%%time
df_growth_signals_2y = hub.growth_signals(variant='latest',
                                          func=sf.avg_ttm_2y)

#cell 24
df_growth_signals_2y.dropna().head()

#cell 25
## Valuation Signals

Now we calculate valuation signals for the stocks, such as P/E, P/Sales, etc. These are calculated from the share-prices and data from the financial reports. Because the data-hub has already loaded the required datasets in the function-calls above, the data is merely reused here, and the data-hub can proceed directly to computing the signals.

#cell 26
%%time
df_val_signals = hub.val_signals(variant='latest')

#cell 27
df_val_signals.dropna().head()

#cell 28
We then pass the argument `func=sf.avg_ttm_2y` to `hub.val_signals` so as to calculate the valuation signals using 2-year averages of the financial data. We then get another DataFrame with e.g. P/E and P/Sales ratios calculated from the 2-year average Earnings and Sales.

#cell 29
%%time
df_val_signals_2y = hub.val_signals(variant='latest',
                                    func=sf.avg_ttm_2y)

#cell 30
df_val_signals_2y.dropna().head()

#cell 31
## Combine Signals

We now combine all the basic signals into a single DataFrame:

#cell 32
# Combine the DataFrames.
dfs = [df_fin_signals, df_growth_signals, df_val_signals]
df_signals = pd.concat(dfs, axis=1)

# Show the result.
df_signals.head()

#cell 33
Then we combine all the signals for multi-year averages into another DataFrame:

#cell 34
# Combine the DataFrames.
dfs = [df_fin_signals_2y, df_growth_signals_2y, df_val_signals_2y]
df_signals_2y = pd.concat(dfs, axis=1)

# Show the result.
df_signals_2y.head()

#cell 35
## Screener for Net-Net Stocks

This is an old investment strategy used by Ben Graham who was the teacher of Warren Buffett, who also used the strategy when he started investing. The idea is to buy stocks that are cheaper than a conservative estimate of their liquidation value. In normal market conditions, few companies have stocks that trade at such low prices, and there may be very good reasons why the stocks are so cheap. But during market panics, it is sometimes possible to buy decent stocks at such low prices.

The Net-Net formula is:

$$
    NetNet = Cash\ \&\ Equiv + 0.75 \cdot Receivables \\
    + 0.5 \cdot Inventories - Total\ Liabilities
$$

This means P/NetNet ratios between 0 and 1 indicate the stocks are trading at a discount to their estimated liquidation values. The lower the P/NetNet ratio, the cheaper the stock is.

We create the stock-screener for Net-Net stocks, by making a boolean mask for the rows in the DataFrame with signals that meet the criteria: P/NetNet > 0 and P/NetNet < 1

#cell 36
mask = (df_signals[P_NETNET] > 0) & (df_signals[P_NETNET] < 1)

#cell 37
Rows that satisfy the screener-condition have a value of `True` and rows that do not meet the condition have a value of `False`.

#cell 38
mask.head()

#cell 39
We can then use the boolean mask to select matching rows in the signal DataFrame, and show the P/NetNet signal:

#cell 40
df_signals.loc[mask, P_NETNET]

#cell 41
Note that some of the dates are not recent, so we can remove all rows with dates that are older than e.g. 30 days, by creating another boolean mask.

#cell 42
# Oldest date that is allowed for a row.
date_limit = datetime.now() - timedelta(days=30)

# Load the latest share-prices from the data-hub.
df_prices_latest = hub.load_shareprices(variant='latest')

# Boolean mask for the tickers that satisfy this condition.
mask_date_limit = (df_prices_latest.reset_index(DATE)[DATE] > date_limit)

# Show the result.
mask_date_limit.head()

#cell 43
We can then combine the screener-mask and the date-mask:

#cell 44
mask &= mask_date_limit

#cell 45
And then we can show the recent stock-prices that are trading at Net-Net discounts:

#cell 46
df_signals.loc[mask, P_NETNET]

#cell 47
## Screener for Many Criteria

It is very easy to combine many criteria in the stock-screener. Let use start with the condition that the Market Capitalization must be more then USD 1 billion:

#cell 48
mask = (df_signals[MARKET_CAP] > 1e9)

#cell 49
Then let us add criteria for the Current Ratio and Debt Ratio calculated from the latest financial reports, as well as the quarterly sales-growth year-over-year.

We combine all these criteria simply by generating the corresponding boolean masks, and doing the logical-and with the previous mask, thereby accumulating multiple criteria.

#cell 50
mask &= (df_signals[CURRENT_RATIO] > 2)
mask &= (df_signals[DEBT_RATIO] < 0.5)
mask &= (df_signals[SALES_GROWTH_YOY] > 0.1)

#cell 51
We can also create screener-criteria using the 2-year average signals, e.g. the P/E and P/FCF ratios which use 2-year average Earnings and FCF. We can combine screener-criteria from `df_signals` and `df_signals_2y` because their indices are compatible.

#cell 52
mask &= (df_signals_2y[PE] < 20)
mask &= (df_signals_2y[PFCF] < 20)
mask &= (df_signals_2y[ROA] > 0.03)
mask &= (df_signals_2y[ROE] > 0.15)
mask &= (df_signals_2y[NET_PROFIT_MARGIN] > 0.0)
mask &= (df_signals_2y[SALES_GROWTH] > 0.1)

#cell 53
Finally we can ensure that we only get the stocks with recent share-prices:

#cell 54
mask &= mask_date_limit

#cell 55
These are the stocks and signals matching all these criteria:

#cell 56
df_signals[mask]

#cell 57
We can also show a sub-set of all the signals and sort e.g. by the P/FCF ratios:

#cell 58
columns = [PFCF, PE, ROA, ROE, CURRENT_RATIO, DEBT_RATIO]
df_signals.loc[mask, columns].sort_values(by=PFCF, ascending=True)

#cell 59
## Handling NaN Signal-Values

The signals are calculated from various financial data using mathematical formulas. If any data-item in the formula is NaN (Not-a-Number) then the result of the entire formula is also NaN, and then the screener-condition automatically evaluates to False, so the company is excluded from the results of the stock-screener.

For example, the Debt Ratio (`DEBT_RATIO`) is calculated from Short Term Debt (`ST_DEBT`), Long Term Debt (`LT_DEBT`) and Total Assets (`TOTAL_ASSETS`). If just one of these numbers is NaN, then the resulting Debt Ratio is also NaN and the screener-condition for this signal will always evaluate to False, so the company is excluded from the screener's results.

You might think that a solution would simply be to use `fillna(0)` on all the data-items before calculating the signals. This may work for some formulas and for some uses of the signals, but it is not a generally valid solution, as it may severely distort the signals.

Consider for example the ticker AMZN, where all data for Short Term Debt is missing in all the reports, while the Long Term Debt is only missing in some reports. If you look at the data, it seems most likely that this is a data-error, and the Long Term Debt should actually be several billions of dollars. If we were to replace these missing values with zeros, then we would get very misleading Debt Ratios.

In this example, AMZN had actually not reported these numbers in some of their quarterly reports. That is why the values are missing in the data.

#cell 60
# Load the TTM Balance Sheets from the data-hub.
df_balance_ttm = hub.load_balance(variant='ttm')

# Show the relevant data.
columns = [ST_DEBT, LT_DEBT, TOTAL_ASSETS]
df_balance_ttm.loc['AMZN', columns]['2010':'2013']

#cell 61
A simple solution is to ignore signals that are NaN. For example, we could have the following criteria:

#cell 62
# Start the screener with a market-cap condition.
mask = (df_signals[MARKET_CAP] > 1e9)

# Ensure share-prices are recent.
mask &= mask_date_limit

# Screener criteria where NaN signals are ignored.
mask &= ((df_signals[CURRENT_RATIO] > 2) | (df_signals[CURRENT_RATIO].isnull()))
mask &= ((df_signals[DEBT_RATIO] < 0.5) | (df_signals[DEBT_RATIO].isnull()))
mask &= ((df_signals[PE] < 20) | (df_signals[PE].isnull()))
mask &= ((df_signals[PFCF] < 20) | (df_signals[PFCF].isnull()))
mask &= ((df_signals[ROA] > 0.03) | (df_signals[ROA].isnull()))
mask &= ((df_signals[ROE] > 0.15) | (df_signals[ROE].isnull()))
mask &= ((df_signals[NET_PROFIT_MARGIN] > 0.0) | (df_signals[NET_PROFIT_MARGIN].isnull()))
mask &= ((df_signals[SALES_GROWTH] > 0.1) | (df_signals[SALES_GROWTH].isnull()))

#cell 63
The following shows the stocks whose signals match these criteria. You can see that some of the signals are NaN, but the stocks are still included in the results, because the screener just ignores NaN values:

#cell 64
columns = [PFCF, PE, ROA, ROE, CURRENT_RATIO, DEBT_RATIO]
df_signals.loc[mask, columns].sort_values(by=PE, ascending=True)

#cell 65
## Back-Testing

We will now test if the stock-screener would have been able to find profitable investments in the past. You can use this method to test which screener-criteria are important and which ones are not, so as to gradually refine your stock-screener.

First we need to calculate the signals for all the historical daily data-points. We will screen for P/E ratios, Sales Growth, Return on Assets, etc., and these signals are highly susceptible to short-term variations, so we will use their 3-year averages instead.

Then we calculate the 1-3 year average annualized log-returns for all the stocks, which is the investment horizon we will consider when testing if the screener's criteria could discover profitable investments in the past. Note that we are calculating the average log-returns for all 1-3 year investment periods, because the log-returns are easier to calculate using Pandas and numpy.

Calculating the signals and returns takes a few minutes to run.

#cell 66
%%time
# Calculate the signals for all daily data-points.
# We pass the arg func=sf.avg_ttm_3y to get the 3-year averages.
df_fin_signals = hub.fin_signals(variant='daily', func=sf.avg_ttm_3y)
df_growth_signals = hub.growth_signals(variant='daily', func=sf.avg_ttm_3y)
df_val_signals = hub.val_signals(variant='daily', func=sf.avg_ttm_3y)

# Combine all the signals into a single DataFrame.
dfs = [df_fin_signals, df_growth_signals, df_val_signals]
df_signals = pd.concat(dfs, axis=1)

# Remove outliers in the signals by clipping / limiting them.
df_signals = sf.winsorize(df=df_signals, clip=True)

# Name of the data-column for the stock-returns.
TOTAL_RETURN_1_3Y = 'Total Return 1-3 Years'

# Calculate the mean log-returns for all 1-3 year periods.
df_returns_1_3y = \
    hub.mean_log_returns(name=TOTAL_RETURN_1_3Y,
                         future=True, annualized=True,
                         min_years=1, max_years=3)

# Combine the signals and mean log-returns into a single DataFrame.
dfs = [df_signals, df_returns_1_3y]
df_sig_rets = pd.concat(dfs, axis=1)

#cell 67
We can now create a stock-screener similar to how we did it above. We will use nearly the same criteria as above with only minor changes. The result is a Pandas Series with boolean values for each stock and each trading-day, telling us whether or not the screener's criteria were met for that stock on that particular day. We can then use this boolean mask to select only the rows where the screener's criteria were met.

#cell 68
# Start the screener with a market-cap condition.
mask = (df_sig_rets[MARKET_CAP] > 1e9)

# Screener criteria where NaN signals are ignored.
mask &= ((df_sig_rets[CURRENT_RATIO] > 2) | (df_sig_rets[CURRENT_RATIO].isnull()))
mask &= ((df_sig_rets[DEBT_RATIO] < 0.5) | (df_sig_rets[DEBT_RATIO].isnull()))
mask &= (((df_sig_rets[PE] > 0) & (df_sig_rets[PE] < 20)) | (df_sig_rets[PE].isnull()))
mask &= (((df_sig_rets[PFCF] > 0) & (df_sig_rets[PFCF] < 20)) | (df_sig_rets[PFCF].isnull()))
mask &= ((df_sig_rets[ROA] > 0.03) | (df_sig_rets[ROA].isnull()))
mask &= ((df_sig_rets[ROE] > 0.15) | (df_sig_rets[ROE].isnull()))
mask &= ((df_sig_rets[NET_PROFIT_MARGIN] > 0.0) | (df_sig_rets[NET_PROFIT_MARGIN].isnull()))
mask &= ((df_sig_rets[SALES_GROWTH] > 0.0) | (df_sig_rets[SALES_GROWTH].isnull()))
    
# Select the rows that satisfy the screener criteria.
df_match = df_sig_rets.loc[mask]

#cell 69
The table below shows some basic statistics for the historical stock-returns when the screener's criteria were met. Because of outliers in the data, it is probably best to ignore the means and instead consider the medians.

#cell 70
# Combine basic statistics for the stock-returns and show them.
data = \
{
    'Screener': df_match[TOTAL_RETURN_1_3Y].describe(),
    'No Screener': df_sig_rets[TOTAL_RETURN_1_3Y].describe()
}
pd.DataFrame(data).round(3)

#cell 71
When the screener was used, the median annualized return was several percentage-points higher than without the screener. These are log-returns but in this range of values, they are nearly the same as the non-log returns.

The standard deviation was significantly lower when using the screener, even though the returns are significantly higher. This is contrary to what academic finance theory claims possible, because they believe that the standard deviation measures investment risk, and risk must be inversely proportional to returns. But the standard deviation is an absurd measure of investment risk as explained [here](https://www.youtube.com/watch?v=wr8NzThfpAE) and [here](https://www.youtube.com/watch?v=DzTlH6ipx98).

Also note that there are millions of rows in the original dataset, but there is only a fraction of those rows that meet the screener's criteria.

Let us now make plots of the signals versus stock-returns. First we need a helper-function:

#cell 72
def plot_scatter(df, x, y, hue=None, num_samples=5000):
    """
    Make a scatter-plot using a random sub-sample of the data.
    
    :param df:
        Pandas DataFrame with columns named `x`, `y` and `hue`.

    :param x:
        String with column-name for the x-axis.

    :param y:
        String with column-name for the y-axis.

    :param hue:
        Either None or string with column-name for the hue.

    :param num_samples:
        Int with number of random samples for the scatter-plot.

    :return:
        matplotlib Axes object
    """

    # Select the relevant columns from the DataFrame.
    if hue is None:
        df = df[[x, y]]
    else:
        df = df[[x, y, hue]]
        
    # Remove empty rows.
    df = df.dropna()

    # Only plot a random sample of the data-points?
    if num_samples is not None and len(df) > num_samples:
        idx = np.random.randint(len(df), size=num_samples)
        df = df.iloc[idx]
        
    # Ensure the plotting area is a square.
    plt.figure(figsize=(5,5))

    # Make the scatter-plot.
    ax = sns.scatterplot(x=x, y=y, hue=hue, s=20,
                         data=df.reset_index())

    # Move legend for the hue.
    if hue is not None:
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), ncol=1)
    
    return ax

#cell 73
Let us try and plot the P/E ratio on the x-axis and the average stock-returns for all 1-3 year periods on the y-axis. The hue is the Return on Equity. This is just a random blob of points:

#cell 74
plot_scatter(df=df_sig_rets, x=PE, y=TOTAL_RETURN_1_3Y, hue=ROE);

#cell 75
Note that these scatter-plots only use a sample of 5000 randomly selected points, because there is actually more than 1.5 million data-points, which would make the plotting very slow (or even crash the program), and even if it worked, it would make the plot very messy to look at. Because of the random sampling, the plots may change slightly if you run the function again, but the plots should generally be representative of the entire data-set.

Now let us try and restrict the plot to only show the data-points where the stock-screener's criteria were met. This is still a blob of points, but perhaps not quite as random as before. The points are also shifted upwards because they tend to have more positive stock-returns.

#cell 76
plot_scatter(df=df_match, x=PE, y=TOTAL_RETURN_1_3Y, hue=ROE);

#cell 77
If we plot it for only some of the tickers, then we can see a characteristic downward-trending slope, which is the topic of [this research](https://www.youtube.com/playlist?list=PL9Hr9sNUjfsmlHaWuVxIA0pKL1yjryR0Z). It turns out there is a mathematical reason why we are observing this downwards slope in the data, as explained [here](https://www.youtube.com/watch?v=OFCHKYgGJRA). The slope always has the same shape, it is just shifted up or down depending on the company's future sales and earnings growth, and its future stock-valuation ratio.

#cell 78
# Get all tickers that match the screener-criteria at some point.
all_tickers = df_match[[PE, TOTAL_RETURN_1_3Y]].dropna().reset_index()[TICKER].unique()

# Randomly select some of those tickers.
tickers = np.random.choice(all_tickers, size=20, replace=False)

# Make the scatter-plot for only those tickers.
plot_scatter(df=df_match.loc[tickers].reset_index(),
             x=PE, y=TOTAL_RETURN_1_3Y, hue=TICKER);

#cell 79
## Optimization

We can also automatically optimize the parameters of the screener-criteria by using a heuristic optimizer such as [Differential Evolution](https://en.wikipedia.org/wiki/Differential_evolution) as implemented in the [scipy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.differential_evolution.html) library. Because this optimizer does not require the mathematical gradient of the problem, it can often optimize very hard problems that cannot be made into simple mathematical formulas.

We will use a simplified screener in this example. First we define the boundaries for the screener's parameters:

#cell 80
bounds = \
[
    (1e6, 1e12),  # mcap_min
    (0.0, 1.0),   # debt_ratio_max
    (0.0, 30.0),  # pe_min
    (0.0, 50.0),  # pe_max
    (0.0, 1.0),   # roa_min
    (0.0, 1.0),   # roe_min
    (-0.2, 0.5),  # sales_growth_min
]

#cell 81
Then we define a function for running the stock-screener, which returns the rows from `df_sig_rets` that match the screener-criteria with the given parameters. This is a simpler version of the stock-screeners we made above.

#cell 82
def screener(x):
    """
    Run the stock-screener with the given parameters x
    and return only the rows that satisfy the screen-criteria.
    
    :param x: Array with parameters for the screener.
    :return: Pandas DataFrame.
    """

    # Unpack the screener-parameters.
    mcap_min, debt_ratio_max, pe_min, pe_max, roa_min, \
        roe_min, sales_growth_min = x
    
    # Start the screener with a market-cap condition.
    mask = (df_sig_rets[MARKET_CAP] > mcap_min)

    # Screener criteria where NaN signals are ignored.
    mask &= ((df_sig_rets[DEBT_RATIO] < debt_ratio_max) | (df_sig_rets[DEBT_RATIO].isnull()))
    mask &= ((df_sig_rets[ROA] > roa_min) | (df_sig_rets[ROA].isnull()))
    mask &= ((df_sig_rets[ROE] > roe_min) | (df_sig_rets[ROE].isnull()))
    mask &= (((df_sig_rets[PE] > pe_min) & (df_sig_rets[PE] < pe_max)) | (df_sig_rets[PE].isnull()))
    mask &= ((df_sig_rets[SALES_GROWTH] > sales_growth_min) | (df_sig_rets[SALES_GROWTH].isnull()))

    # Select the rows that satisfy the screener criteria.
    df_match = df_sig_rets.loc[mask]
    
    return df_match

#cell 83
Then we define the objective function (aka. cost or fitness function) that must be *minimized*. This basically just wraps the screener-function above and measures the median returns for stocks that match the screener-criteria with the given parameters.

The objective function also penalizes screener-parameters that result in too few matching stocks or too few data-points, so as to avoid over-fitting the screener-parameters to just a few stocks that happened to perform really well during this period.

#cell 84
def objective(x):
    """
    Function whose return-value must be minimized by changing
    the screener parameters x.
    
    :param x: Array with parameters for the screener.
    :return: Float to be minimized.
    """

    # Run the stock-screener and get the matching rows, which
    # contain a Ticker and Date as well as the signals and
    # future stock-returns.
    df_match = screener(x)

    # Did the stock-screener find any matching rows?
    if len(df_match)>0:
        # Get the stock-returns for the matching rows.
        # Drop NaN-rows because we count the rows further below.
        df_returns = df_match[TOTAL_RETURN_1_3Y].dropna()

        # The optimization objective is the MEDIAN stock-return.
        # We use this instead of the mean to avoid outliers.
        # It is negated because the optimizer performs
        # minimization, but we are actually interested in
        # maximizing the median stock-return.
        objective = -df_returns.median()
    
        # Now we will penalize the objective to try and find
        # stock-screener parameters that result in certain
        # characteristics for the matching stocks.
        
        # Initialize the penalty. This number will be lowered
        # towards zero in the tests below, and finally multiplied
        # with the objective value.
        penalty = 1.0

        # Gradually penalize when there are fewer data-points.
        limit = 50000
        if len(df_returns) < limit:
            penalty *= len(df_returns) / limit

        # Gradually penalize when there are fewer unique stocks.
        num_tickers = len(df_returns.reset_index()[TICKER].unique())
        limit = 100
        if num_tickers < limit:
            penalty *= num_tickers / limit

        # Gradually penalize when there are fewer stocks per day
        # on average.
        num_per_day = df_returns.reset_index()[[DATE, TICKER]].groupby(DATE).count()
        mean = num_per_day[TICKER].mean()
        limit = 50
        if mean < limit:
            penalty *= mean / limit

        # Gradually penalize when the P/E signal is missing / NaN.
        penalty *= len(df_match[PE].dropna()) / len(df_match)

        # Apply the penalty to the objective function.
        objective *= penalty
    else:
        # The stock-screener did not find any matching rows,
        # so use a very high value. A small random value is
        # added to avoid premature stagnation of the optimizer,
        # in case all trials in its populations have the exact
        # same objective value.
        objective = 1000.0 + np.random.rand()
        
    return objective

#cell 85
We will also need a small helper-function for printing the best-found screener-parameters:

#cell 86
def print_parameters(x):
    """
    Print the parameters for the screener-criteria.
    
    :param x: Array with parameters for the screener.
    """
    
    # Unpack the parameters.
    mcap_min, debt_ratio_max, pe_min, pe_max, roa_min, \
        roe_min, sales_growth_min = x

    # Print the parameters.
    print('Market-Cap Min:   {:.0}'.format(mcap_min))
    print('Debt Ratio Max:   {:.2f}'.format(debt_ratio_max))
    print('P/E Min:          {:.1f}'.format(pe_min))
    print('P/E Max:          {:.1f}'.format(pe_max))
    print('ROA Min:          {:.2f}'.format(roa_min))
    print('ROE Min:          {:.2f}'.format(roe_min))
    print('Sales Growth Min: {:.2f}'.format(sales_growth_min))

#cell 87
We can then run the optimization. This may take several minutes on a quad-core CPU.

#cell 88
%%time
# Only do a short run if this is run using pytest.
# This is to save time during automated testing.
maxiter = 2 if running_pytest else 30

# Run the optimization.
# Note the increased population-size which seemed to
# perform better than the default choice of only 15.
result = differential_evolution(func=objective, bounds=bounds,
                                popsize=30, disp=True,
                                maxiter=maxiter)

# Get the best-found screener parameters.
best_parameters = result.x

#cell 89
These are the optimized screener-parameters that gave the best investment performance:

#cell 90
print_parameters(x=best_parameters)

#cell 91
We can then try and run the stock-screener with the optimized parameters, and make a scatter-plot of the matching P/E ratios versus the average 1-3 year stock-returns:

#cell 92
# Run the screener with the optimized parameters,
# and get the rows that satisfy the screener-criteria.
df_match = screener(best_parameters)

# Scatter-plot of the P/E versus stock-returns.
plot_scatter(df=df_match, x=PE, y=TOTAL_RETURN_1_3Y,
             hue=SALES_GROWTH);

#cell 93
We can also print the basic statistics for the average 1-3 year stock-returns from the screener with the optimized parameters. Note that these are actually worse than for the stock-screener and parameters we had made further above. The reason is probably that the optimized screener-parameters also try to ensure that the screener finds a diverse set of stocks, and that the P/E signals are actually present; while the stock-screener further above would also select stocks where the P/E signal was NaN (Not-a-Number).

#cell 94
df_match[TOTAL_RETURN_1_3Y].describe()

#cell 95
We can also show how many stocks the screener found for every single day. We had programmed the `objective()` function so it would penalize the screener-parameters, if they resulted in there being an average of fewer than 50 stocks that matched the screener every day.

#cell 96
df_match[TOTAL_RETURN_1_3Y].dropna().groupby(DATE).count().plot(grid=True);

#cell 97
For every day, we can show the average 1-3 year return for all the stocks matching the screener with the optimized parameters. We can see that the screener seems to work better in some periods than others.

#cell 98
df_match[TOTAL_RETURN_1_3Y].groupby(DATE).mean().plot();

#cell 99
## Research Ideas

The screener optimization shown above can be extended in many different ways. Here are a few ideas to get you started:

- Split the data-set into training- and test-sets as shown in the other SimFin tutorials on Machine Learning. Does the screener work just as well on stock-data that it has not seen during the training?

- Create an *ensemble* of stock-screeners by making different screeners that are specialized for different things, e.g. one screener could be specialied for high-growth companies, and another screener could be specialized for under-valued companies. You can also run the optimization several times for each screener, and then average all of the results when building your investment portfolio.

- Use multi-objective optimization to find optimal trade-offs e.g. between average returns and probability of loss. You can modify this [implementation](https://github.com/Hvass-Labs/FinanceOps/blob/master/04_Multi-Objective_Portfolio_Optimization.ipynb).

- Use Genetic Programming to optimize both the screener-parameters and the entire screener-formula, to find which signals should be used, how they should be used, and what the parameters should be.

Please share your results with the rest of the community, that is what SimFin is made for!

#cell 100
## License (MIT)

This is published under the
[MIT License](https://github.com/simfin/simfin-tutorials/blob/master/LICENSE.txt)
which allows very broad use for both academic and commercial purposes.

You are very welcome to modify and use this source-code in your own project. Please keep a link to the [original repository](https://github.com/simfin/simfin-tutorials).


