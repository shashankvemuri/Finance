from sklearn.ensemble import IsolationForest
class IsolationModel:
    """
        Simple Isolation Model based on contamination
    """

    def __init__(self, data):
        self.normalized_data = (data - data.mean()) / data.std()
        self.iso = IsolationForest(contamination=.001, behaviour='new')
        self.iso.fit(self.normalized_data)
        self.iso.predict(self.normalized_data)

    def predict_outlier(self, data):
        return self.iso.predict(data)
    
from models.isolation_model import IsolationModel
import backtrader as bt
import pandas as pd
import numpy as np


class IsolationStrategy(bt.Strategy):
    '''
        Explanation:
        The isolation forest identifies what it deems to be anomalies,
        overbought or oversold opportunities for entry. I append known data
        after fitting the isolation forest for the next day, making it an
        online unsupervised learningalgorithm.
        Current Issue: Positioning, Sizing, Exposure
'''

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self, data):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.dataclose = self.datas[0].close
        self.datavolume = self.datas[0].volume
        self.model_data = pd.read_csv(data)
        self.buyOut = False
        self.sellOut = False
        self.orderPosition = 0
        self.cooldown = 7

    # This is the code that gets copied into the trading system
    def next(self):
        self.log(self.dataclose[0])

        # Construct dataframe to predict
        x = pd.DataFrame(
            data=[[
                self.dataopen[0], self.datahigh[0], self.datalow[0],
                self.dataclose[0], self.datavolume[0]
                ]], columns='Open High Low Close Volume'.split()
        )

        # Create the model with all known data for normalization
        model = IsolationModel(self.model_data)

        # Append today's data for tomorrow's normalization
        self.model_data = self.model_data.append(x, ignore_index=True)

        # Dataframe to help normalize x
        mean_to_normalize = pd.DataFrame(data=[[
            np.mean(self.model_data['Open']), np.mean(self.model_data['High']),
            np.mean(self.model_data['Low']), np.mean(self.model_data['Close']),
            np.mean(self.model_data['Volume'])
            ]], columns='Open High Low Close Volume'.split())

        # Dataframe to help normalize x
        std_to_normalize = pd.DataFrame(data=[[
            np.std(self.model_data['Open']), np.std(self.model_data['High']),
            np.std(self.model_data['Low']), np.std(self.model_data['Close']),
            np.std(self.model_data['Volume'])
            ]], columns='Open High Low Close Volume'.split())

        # x is normalized as a parameter
        normalized_x = (x - mean_to_normalize) / std_to_normalize

        """
        # Write updated Data to CSV - To be included in the live system
        self.model_data.to_csv('FB.csv', index=False)
        """

        # Same but opposite conditions
        if model.predict_outlier(normalized_x) == -1 & \
                (self.dataclose[0] > np.mean(self.model_data['Close'])):
            self.log('SELL CREATE, %.2f' % self.dataclose[0])
            if not self.orderPosition == 0:
                self.sell(size=1)
                self.orderPosition -= 1

        # Same but opposite conditions
        if model.predict_outlier(normalized_x) == -1 & \
                (self.dataclose[0] < np.mean(self.model_data['Close'])) & \
                (self.cooldown == 0):
            self.log('BUY CREATE, %.2f' % self.dataclose[0])
            self.buy(size=1)
            self.orderPosition += 1
            self.cooldown = 7
        if self.cooldown > 0:
            self.cooldown -= 1

import backtrader as bt
import pyfolio as pf


def backtesting_engine(symbol, strategy, fromdate, todate, args=None):
    """
        Primary function for backtesting, not entirely parameterized
    """

    # Backtesting Engine
    cerebro = bt.Cerebro()

    # Add a Strategy if no Data Required for the model
    if args is None:
        cerebro.addstrategy(strategy)
    # If the Strategy requires a Model and therefore data
    elif args is not None:
        cerebro.addstrategy(strategy, args)

    # Retrieve Data from Alpaca
    data = bt.feeds.YahooFinanceData(
        dataname=symbol,
        fromdate=fromdate,  # datetime.date(2015, 1, 1)
        todate=todate,  # datetime.datetime(2016, 1, 1)
        reverse=False
    )

    # Add Data to Backtesting Engine
    cerebro.adddata(data)

    # Set Initial Portfolio Value
    cerebro.broker.setcash(100000.0)

    # Add Analysis Tools
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.PositionsValue, _name='posval')
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')

    # Starting Portfolio Value
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run the Backtesting Engine
    backtest = cerebro.run()

    # Print Analysis and Final Portfolio Value
    print(
        'Final Portfolio Value: %.2f' % cerebro.broker.getvalue()
        )
    print(
        'Return: ', backtest[0].analyzers.returns.get_analysis()
        )
    print(
        'Sharpe Ratio: ', backtest[0].analyzers.sharpe.get_analysis()
        )
    print(
        'System Quality Number: ', backtest[0].analyzers.sqn.get_analysis()
        )
    print(
        'Drawdown: ', backtest[0].analyzers.drawdown.get_analysis()
        )
    print(
        'Active Position Value: ', backtest[0].analyzers.posval.get_analysis()
    )
    print(
        'Pyfolio: ', backtest[0].analyzers.pyfolio.get_analysis()
    )

    # Print Analysis and Final Portfolio Value
    pyfoliozer = backtest[0].analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()

    # See if we can add regular FB data to compare against returns of algo
    pf.create_full_tear_sheet(
        returns, positions=positions, transactions=transactions
        )


# TODO: Create pipeline: Optimization -> Testing essentially
class BacktestingPipeline:
    """
        Pipeline for in sample optimization and out of sample testing
    """
    pass

from datetime import datetime
from strategies.isolation_strategy import IsolationStrategy
from tools.backtesting_tools import backtesting_engine


"""
    Script for backtesting strategies
"""

if __name__ == '__main__':
    # Run backtesting engine
    backtesting_engine(
        'TICKER', IsolationStrategy, args='DATA.csv',
        fromdate=datetime(2018, 1, 1), todate=datetime(2019, 1, 1)
    )
    
