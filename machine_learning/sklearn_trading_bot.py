# Import dependencies
from datetime import datetime
from sklearn.ensemble import IsolationForest
import backtrader as bt
import pandas as pd
import numpy as np
import pyfolio as pf

# Isolation Forest Model Class
class IsolationModel:
    def __init__(self, data):
        normalized_data = (data - data.mean()) / data.std()
        self.iso = IsolationForest(contamination=0.001, behaviour="new")
        self.iso.fit(normalized_data)

    def predict_outlier(self, data):
        return self.iso.predict(data)

# Trading Strategy Class using Isolation Forest
class IsolationStrategy(bt.Strategy):
    def __init__(self, data):
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.dataclose = self.datas[0].close
        self.datavolume = self.datas[0].volume
        self.model_data = pd.read_csv(data)
        self.orderPosition = 0
        self.cooldown = 7

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()}, {txt}")

    def next(self):
        self.log(self.dataclose[0])
        x = pd.DataFrame([[self.dataopen[0], self.datahigh[0], self.datalow[0], self.dataclose[0], self.datavolume[0]]], 
                         columns=["Open", "High", "Low", "Close", "Volume"])
        self.model_data = self.model_data.append(x, ignore_index=True)
        normalized_x = (x - self.model_data.mean()) / self.model_data.std()
        model = IsolationModel(self.model_data)

        if model.predict_outlier(normalized_x) == -1:
            if self.dataclose[0] > np.mean(self.model_data["Close"]):
                self.log("SELL CREATE, %.2f" % self.dataclose[0])
                if self.orderPosition != 0:
                    self.sell(size=1)
                    self.orderPosition -= 1
            elif self.dataclose[0] < np.mean(self.model_data["Close"]) and self.cooldown == 0:
                self.log("BUY CREATE, %.2f" % self.dataclose[0])
                self.buy(size=1)
                self.orderPosition += 1
                self.cooldown = 7
        if self.cooldown > 0:
            self.cooldown -= 1

# Backtesting Engine
def backtesting_engine(symbol, strategy, args, fromdate, todate):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy, args)
    data = bt.feeds.YahooFinanceData(dataname=symbol, fromdate=fromdate, todate=todate)
    cerebro.adddata(data)
    cerebro.broker.setcash(100000.0)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name="pyfolio")
    print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())
    backtest = cerebro.run()
    print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())
    pyfoliozer = backtest[0].analyzers.getbyname("pyfolio")
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    pf.create_full_tear_sheet(returns, positions=positions, transactions=transactions)

if __name__ == "__main__":
    backtesting_engine(
        "AAPL",
        IsolationStrategy,
        "data.csv",
        datetime(2018, 1, 1),
        datetime(2019, 1, 1),
    )