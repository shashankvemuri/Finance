from fastquant import backtest, get_stock_data
jfc = get_stock_data("JFC", "2018-01-01", "2019-01-01")
backtest('smac', jfc, fast_period=15, slow_period=40)