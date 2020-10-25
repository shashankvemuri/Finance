import yfinance as yf
import ta
import pandas as pd
from datetime import date, timedelta, datetime
from IPython.display import clear_output
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

ticker = 'FSLY'
start_date = '2019-10-23'
end_date = '2020-10-23'

def get_stock_backtest_data(ticker, start, end):
  date_fmt = '%Y-%m-%d'

  start_date_buffer = datetime.strptime(start_date, date_fmt) - timedelta(days=365)
  start_date_buffer = start_date_buffer.strftime(date_fmt)

  df = yf.download(ticker, start=start_date_buffer, end=end_date)

  return df

df = get_stock_backtest_data(ticker, start_date, end_date)
df['CLOSE_PREV'] = df.Close.shift(1)

k_band = ta.volatility.KeltnerChannel(df.High, df.Low, df.Close, 10)

df['K_BAND_UB'] = k_band.keltner_channel_hband().round(4)
df['K_BAND_LB'] = k_band.keltner_channel_lband().round(4)

df[['K_BAND_UB', 'K_BAND_LB']].dropna().head()

df['LONG'] = (df.Close <= df.K_BAND_LB) & (df.CLOSE_PREV > df.K_BAND_LB)
df['EXIT_LONG'] = (df.Close >= df.K_BAND_UB) & (df.CLOSE_PREV < df.K_BAND_UB)

df['SHORT'] = (df.Close >= df.K_BAND_UB) & (df.CLOSE_PREV < df.K_BAND_UB)
df['EXIT_SHORT'] = (df.Close <= df.K_BAND_LB) & (df.CLOSE_PREV > df.K_BAND_LB)

df.LONG = df.LONG.shift(1)
df.EXIT_LONG = df.EXIT_LONG.shift(1)
df.SHORT = df.SHORT.shift(1)
df.EXIT_SHORT = df.EXIT_SHORT.shift(1)

print(df[['LONG', 'EXIT_LONG', 'SHORT', 'EXIT_SHORT']].dropna().head())

def strategy_KeltnerChannel_origin(df, **kwargs):
  n = kwargs.get('n', 10)
  data = df.copy()

  k_band = ta.volatility.KeltnerChannel(data.High, data.Low, data.Close, n)

  data['K_BAND_UB'] = k_band.keltner_channel_hband().round(4)
  data['K_BAND_LB'] = k_band.keltner_channel_lband().round(4)

  data['CLOSE_PREV'] = data.Close.shift(1)
  
  data['LONG'] = (data.Close <= data.K_BAND_LB) & (data.CLOSE_PREV > data.K_BAND_LB)
  data['EXIT_LONG'] = (data.Close >= data.K_BAND_UB) & (data.CLOSE_PREV < data.K_BAND_UB)

  data['SHORT'] = (data.Close >= data.K_BAND_UB) & (data.CLOSE_PREV < data.K_BAND_UB)
  data['EXIT_SHORT'] = (data.Close <= data.K_BAND_LB) & (data.CLOSE_PREV > data.K_BAND_LB)

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)
  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data

df = strategy_KeltnerChannel_origin(df, n=10)

def strategy_BollingerBands(df, **kwargs):
  n = kwargs.get('n', 10)
  n_rng = kwargs.get('n_rng', 2)
  data = df.copy()

  boll = ta.volatility.BollingerBands(data.Close, n, n_rng)

  data['BOLL_LBAND_INDI'] = boll.bollinger_lband_indicator()
  data['BOLL_UBAND_INDI'] = boll.bollinger_hband_indicator()

  data['CLOSE_PREV'] = data.Close.shift(1)

  data['LONG'] = data.BOLL_LBAND_INDI == 1
  data['EXIT_LONG'] = data.BOLL_UBAND_INDI == 1

  data['SHORT'] = data.BOLL_UBAND_INDI == 1
  data['EXIT_SHORT'] = data.BOLL_LBAND_INDI == 1

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)
  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data

# df = get_stock_backtest_data(ticker, start_date, end_date)
# strategy_BollingerBands(df, n=10, n_rng=2)

def strategy_MA(df, **kwargs):
  n = kwargs.get('n', 50)
  ma_type = kwargs.get('ma_type', 'sma')
  ma_type = ma_type.strip().lower()
  data = df.copy()
  
  if ma_type == 'sma':
    sma = ta.trend.SMAIndicator(data.Close, n)
    data['MA'] = sma.sma_indicator().round(4)
  elif ma_type == 'ema':
    ema = ta.trend.EMAIndicator(data.Close, n)
    data['MA'] = ema.ema_indicator().round(4)

  data['CLOSE_PREV'] = data.Close.shift(1)

  data['LONG'] = (data.Close > data.MA) & (data.CLOSE_PREV <= data.MA)
  data['EXIT_LONG'] = (data.Close < data.MA) & (data.CLOSE_PREV >= data.MA)

  data['SHORT'] = (data.Close < data.MA) & (data.CLOSE_PREV >= data.MA)
  data['EXIT_SHORT'] = (data.Close > data.MA) & (data.CLOSE_PREV <= data.MA)

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)
  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data

# df = get_stock_backtest_data(ticker, start_date, end_date)
# strategy_SMA(df, n=10, ma_type='ema')

def strategy_MACD(df, **kwargs):
  n_slow = kwargs.get('n_slow', 26)
  n_fast = kwargs.get('n_fast', 12)
  n_sign = kwargs.get('n_sign', 9)
  data = df.copy()

  macd = ta.trend.MACD(data.Close, n_slow, n_fast, n_sign)

  data['MACD_DIFF'] = macd.macd_diff().round(4)
  data['MACD_DIFF_PREV'] = data.MACD_DIFF.shift(1)

  data['LONG'] = (data.MACD_DIFF > 0) & (data.MACD_DIFF_PREV <= 0)
  data['EXIT_LONG'] = (data.MACD_DIFF < 0) & (data.MACD_DIFF_PREV >= 0)

  data['SHORT'] = (data.MACD_DIFF < 0) & (data.MACD_DIFF_PREV >= 0)
  data['EXIT_SHORT'] = (data.MACD_DIFF > 0) & (data.MACD_DIFF_PREV <= 0)

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)
  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data

# df = get_stock_backtest_data(ticker, start_date, end_date)
# strategy_MACD(df, n_slow=26, n_fast=12, n_sign=9)

def strategy_RSI(df, **kwargs):
  n = kwargs.get('n', 14)
  data = df.copy()

  rsi = ta.momentum.RSIIndicator(data.Close, n)

  data['RSI'] = rsi.rsi().round(4)
  data['RSI_PREV'] = data.RSI.shift(1)

  data['LONG'] = (data.RSI > 30) & (data.RSI_PREV <= 30)
  data['EXIT_LONG'] = (data.RSI < 70) & (data.RSI_PREV >= 70)

  data['SHORT'] = (data.RSI < 70) & (data.RSI_PREV >= 70)
  data['EXIT_SHORT'] = (data.RSI > 30) & (data.RSI_PREV <= 30)

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)
  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data

# df = get_stock_backtest_data(ticker, start_date, end_date)
# strategy_RSI(df, n_slow=26, n_fast=12, n_sign=9)

def strategy_WR(df, **kwargs):
  n = kwargs.get('n', 14)
  data = df.copy()

  wr = ta.momentum.WilliamsRIndicator(data.High, data.Low, data.Close, n)

  data['WR'] = wr.wr().round(4)
  data['WR_PREV'] = data.WR.shift(1)

  data['LONG'] = (data.WR > -80) & (data.WR_PREV <= -80)
  data['EXIT_LONG'] = (data.WR < -20) & (data.WR_PREV >= -20)

  data['SHORT'] = (data.WR < -20) & (data.WR_PREV >= -20)
  data['EXIT_SHORT'] = (data.WR > -80) & (data.WR_PREV <= -80)

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)
  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data

# df = get_stock_backtest_data(ticker, start_date, end_date)
# strategy_WR(df, n_slow=26, n_fast=12, n_sign=9)

def strategy_Stochastic_fast(df, **kwargs):
  k = kwargs.get('k', 20)
  d = kwargs.get('d', 5)
  data = df.copy()

  sto = ta.momentum.StochasticOscillator(data.High, data.Low, data.Close, k, d)

  data['K'] = sto.stoch().round(4)
  data['D'] = sto.stoch_signal().round(4)
  data['DIFF'] = data['K'] - data['D']
  data['DIFF_PREV'] = data.DIFF.shift(1)
  
  data['LONG'] = (data.DIFF > 0) & (data.DIFF_PREV <= 0)
  data['EXIT_LONG'] = (data.DIFF < 0) & (data.DIFF_PREV >= 0)

  data['SHORT'] = (data.DIFF < 0) & (data.DIFF_PREV >= 0)
  data['EXIT_SHORT'] = (data.DIFF > 0) & (data.DIFF_PREV <= 0)

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)
  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data

# df = get_stock_backtest_data(ticker, start_date, end_date)
# strategy_Stochastic_fast(df, k=20, d=5)

def strategy_Stochastic_slow(df, **kwargs):
  k = kwargs.get('k', 20)
  d = kwargs.get('d', 5)
  dd = kwargs.get('dd', 3)
  data = df.copy()

  sto = ta.momentum.StochasticOscillator(data.High, data.Low, data.Close, k, d)

  data['K'] = sto.stoch().round(4)
  data['D'] = sto.stoch_signal().round(4)
  
  ma = ta.trend.SMAIndicator(data.D, dd)
  data['DD'] = ma.sma_indicator().round(4)

  data['DIFF'] = data['D'] - data['DD']
  data['DIFF_PREV'] = data.DIFF.shift(1)
  
  data['LONG'] = (data.DIFF > 0) & (data.DIFF_PREV <= 0)
  data['EXIT_LONG'] = (data.DIFF < 0) & (data.DIFF_PREV >= 0)

  data['SHORT'] = (data.DIFF < 0) & (data.DIFF_PREV >= 0)
  data['EXIT_SHORT'] = (data.DIFF > 0) & (data.DIFF_PREV <= 0)

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)
  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data

# df = get_stock_backtest_data(ticker, start_date, end_date)
# strategy_Stochastic_slow(df, k=20, d=5, dd=3)

def strategy_Ichmoku(df, **kwargs):
  n_conv = kwargs.get('n_conv', 9)
  n_base = kwargs.get('n_base', 26)
  n_span_b = kwargs.get('n_span_b', 26)
  data = df.copy()

  ichmoku = ta.trend.IchimokuIndicator(data.High, data.Low, n_conv, n_base, n_span_b)

  data['BASE'] = ichmoku.ichimoku_base_line().round(4)
  data['CONV'] = ichmoku.ichimoku_conversion_line().round(4)

  data['DIFF'] = data['CONV'] - data['BASE']
  data['DIFF_PREV'] = data.DIFF.shift(1)
  
  data['LONG'] = (data.DIFF > 0) & (data.DIFF_PREV <= 0)
  data['EXIT_LONG'] = (data.DIFF < 0) & (data.DIFF_PREV >= 0)

  data['SHORT'] = (data.DIFF < 0) & (data.DIFF_PREV >= 0)
  data['EXIT_SHORT'] = (data.DIFF > 0) & (data.DIFF_PREV <= 0)

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)
  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data

# df = get_stock_backtest_data(ticker, start_date, end_date)
# strategy_Ichmoku(df, n_conv=9, n_base=26, n_span_b=26)

bt_df = df[(df.index >= start_date) & (df.index <= end_date)]

def prepare_stock_ta_backtest_data(df, start_date, end_date, strategy, **strategy_params):
  df_strategy = strategy(df, **strategy_params)
  bt_df = df_strategy[(df_strategy.index >= start_date) & (df_strategy.index <= end_date)]
  return bt_df

bt_df = prepare_stock_ta_backtest_data(
    df, start_date, end_date, strategy_KeltnerChannel_origin, n=10
    )

bt_df.head()

balance = 1000000
pnl = 0
position = 0

last_signal = 'hold'
last_price = 0
c = 0

trade_date_start = []
trade_date_end = []
trade_days = []
trade_side = []
trade_pnl = []
trade_ret = []

cum_value = []

for index, row in bt_df.iterrows():
    # check and close any positions
    if row.EXIT_LONG and last_signal == 'long':
      trade_date_end.append(row.name)
      trade_days.append(c)

      pnl = (row.Open - last_price) * position
      trade_pnl.append(pnl)
      trade_ret.append((row.Open / last_price - 1) * 100)
      
      balance = balance + row.Open * position
      
      position = 0
      last_signal = 'hold'

      c = 0
    
    elif row.EXIT_SHORT and last_signal == 'short':
      trade_date_end.append(row.name)
      trade_days.append(c)
      
      pnl = (row.Open - last_price) * position
      trade_pnl.append(pnl)
      trade_ret.append((last_price / row.Open - 1) * 100)

      balance = balance + pnl

      position = 0
      last_signal = 'hold'

      c = 0

    # check signal and enter any possible position
    if row.LONG and last_signal != 'long':
      last_signal = 'long'
      last_price = row.Open
      trade_date_start.append(row.name)
      trade_side.append('long')

      position = int(balance / row.Open)
      cost = position * row.Open
      balance = balance - cost

      c = 0

    elif row.SHORT and last_signal != 'short':
      last_signal = 'short'
      last_price = row.Open
      trade_date_start.append(row.name)
      trade_side.append('short')

      position = int(balance / row.Open) * -1
      
      c = 0
      
    # compute market value and count days for any possible poisition
    if last_signal == 'hold':
      market_value = balance
    elif last_signal == 'long':
      c = c + 1
      market_value = position * row.Close + balance
    else: 
      c = c + 1
      market_value = (row.Close - last_price) * position + balance
    
    cum_value.append(market_value)

cum_ret_df = pd.DataFrame(cum_value, index=bt_df.index, columns=['CUM_RET'])
cum_ret_df['CUM_RET'] = (cum_ret_df.CUM_RET / 1000000 - 1) * 100
cum_ret_df['BUY_HOLD'] = (bt_df.Close / bt_df.Open.iloc[0] - 1) * 100
cum_ret_df['ZERO'] = 0
cum_ret_df.plot(figsize=(15, 5))

print(cum_ret_df.iloc[[-1]].round(2))

size = min(len(trade_date_start), len(trade_date_end))

tarde_dict = {
    'START': trade_date_start[:size],
    'END': trade_date_end[:size],
    'SIDE': trade_side[:size],
    'DAYS': trade_days[:size],
    'PNL': trade_pnl[:size],
    'RET': trade_ret[:size]
}

trade_df = pd.DataFrame(tarde_dict)
print(trade_df.head())

num_trades = trade_df.groupby('SIDE').count()[['START']]
num_trades_win = trade_df[trade_df.PNL > 0].groupby('SIDE').count()[['START']]

avg_days = trade_df.groupby('SIDE').mean()[['DAYS']]

avg_ret = trade_df.groupby('SIDE').mean()[['RET']]
avg_ret_win = trade_df[trade_df.PNL > 0].groupby('SIDE').mean()[['RET']]
avg_ret_loss = trade_df[trade_df.PNL < 0].groupby('SIDE').mean()[['RET']]

std_ret = trade_df.groupby('SIDE').std()[['RET']]

detail_df = pd.concat([
                       num_trades, num_trades_win, avg_days,
                       avg_ret, avg_ret_win, avg_ret_loss, std_ret
                       ], axis=1, sort=False)

detail_df.columns = [
                     'NUM_TRADES', 'NUM_TRADES_WIN', 'AVG_DAYS', 
                     'AVG_RET', 'AVG_RET_WIN', 'AVG_RET_LOSS', 'STD_RET'
                     ]
print(detail_df.round(2))

#Stop Loss

balance = 1000000
pnl = 0
position = 0

stop_loss_lvl = -2

last_signal = 'hold'
last_price = 0
c = 0

trade_date_start = []
trade_date_end = []
trade_days = []
trade_side = []
trade_pnl = []
trade_ret = []

cum_value = []

for index, row in bt_df.iterrows():
    # check and close any positions
    if row.EXIT_LONG and last_signal == 'long':
      trade_date_end.append(row.name)
      trade_days.append(c)

      pnl = (row.Open - last_price) * position
      trade_pnl.append(pnl)
      trade_ret.append((row.Open / last_price - 1) * 100)
      
      balance = balance + row.Open * position
      
      position = 0
      last_signal = 'hold'

      c = 0
    
    elif row.EXIT_SHORT and last_signal == 'short':
      trade_date_end.append(row.name)
      trade_days.append(c)
      
      pnl = (row.Open - last_price) * position
      trade_pnl.append(pnl)
      trade_ret.append((last_price / row.Open - 1) * 100)

      balance = balance + pnl

      position = 0
      last_signal = 'hold'

      c = 0


    # check signal and enter any possible position
    if row.LONG and last_signal != 'long':
      last_signal = 'long'
      last_price = row.Open
      trade_date_start.append(row.name)
      trade_side.append('long')

      position = int(balance / row.Open)
      cost = position * row.Open
      balance = balance - cost

      c = 0

    elif row.SHORT and last_signal != 'short':
      last_signal = 'short'
      last_price = row.Open
      trade_date_start.append(row.name)
      trade_side.append('short')

      position = int(balance / row.Open) * -1
      
      c = 0
    

    # check stop loss
    if last_signal == 'long' and c > 0 and (row.Low / last_price - 1) * 100 <= stop_loss_lvl:
      c = c + 1

      trade_date_end.append(row.name)
      trade_days.append(c)

      stop_loss_price = last_price + round(last_price * (stop_loss_lvl / 100), 4)

      pnl = (stop_loss_price - last_price) * position
      trade_pnl.append(pnl)
      trade_ret.append((stop_loss_price / last_price - 1) * 100)
      
      balance = balance + stop_loss_price * position
      
      position = 0
      last_signal = 'hold'

      c = 0

    elif last_signal == 'short' and c > 0 and (last_price / row.High - 1) * 100 <= stop_loss_lvl:
      c = c + 1

      trade_date_end.append(row.name)
      trade_days.append(c)
      
      stop_loss_price = last_price - round(last_price * (stop_loss_lvl / 100), 4)

      pnl = (stop_loss_price - last_price) * position
      trade_pnl.append(pnl)
      trade_ret.append((last_price / stop_loss_price - 1) * 100)

      balance = balance + pnl

      position = 0
      last_signal = 'hold'

      c = 0


    # compute market value and count days for any possible poisition
    if last_signal == 'hold':
      market_value = balance
    elif last_signal == 'long':
      c = c + 1
      market_value = position * row.Close + balance
    else: 
      c = c + 1
      market_value = (row.Close - last_price) * position + balance
    
    cum_value.append(market_value)

cum_ret_df = pd.DataFrame(cum_value, index=bt_df.index, columns=['CUM_RET'])
cum_ret_df['CUM_RET'] = (cum_ret_df.CUM_RET / 1000000 - 1) * 100
cum_ret_df['BUY_HOLD'] = (bt_df.Close / bt_df.Open.iloc[0] - 1) * 100
cum_ret_df['ZERO'] = 0
cum_ret_df.plot(figsize=(15, 5))

print(cum_ret_df.iloc[[-1]].round(2))

size = min(len(trade_date_start), len(trade_date_end))

tarde_dict = {
    'START': trade_date_start[:size],
    'END': trade_date_end[:size],
    'SIDE': trade_side[:size],
    'DAYS': trade_days[:size],
    'PNL': trade_pnl[:size],
    'RET': trade_ret[:size]
}

trade_df = pd.DataFrame(tarde_dict)
print(trade_df.head())

num_trades = trade_df.groupby('SIDE').count()[['START']]
num_trades_win = trade_df[trade_df.PNL > 0].groupby('SIDE').count()[['START']]

avg_days = trade_df.groupby('SIDE').mean()[['DAYS']]

avg_ret = trade_df.groupby('SIDE').mean()[['RET']]
avg_ret_win = trade_df[trade_df.PNL > 0].groupby('SIDE').mean()[['RET']]
avg_ret_loss = trade_df[trade_df.PNL < 0].groupby('SIDE').mean()[['RET']]

std_ret = trade_df.groupby('SIDE').std()[['RET']]

detail_df = pd.concat([
                       num_trades, num_trades_win, avg_days,
                       avg_ret, avg_ret_win, avg_ret_loss, std_ret
                       ], axis=1, sort=False)

detail_df.columns = [
                     'NUM_TRADES', 'NUM_TRADES_WIN', 'AVG_DAYS', 
                     'AVG_RET', 'AVG_RET_WIN', 'AVG_RET_LOSS', 'STD_RET'
                     ]
print(detail_df.round(2))

mv_df = pd.DataFrame(cum_value, index=bt_df.index, columns=['MV'])
print(mv_df.head())

days = len(mv_df)

roll_max = mv_df.MV.rolling(window=days, min_periods=1).max()
drawdown_val = mv_df.MV - roll_max
drawdown_pct = (mv_df.MV / roll_max - 1) * 100

print("Max Drawdown Value:", round(drawdown_val.min(), 0))
print("Max Drawdown %:", round(drawdown_pct.min(), 2))

def run_stock_ta_backtest(bt_df, stop_loss_lvl=None):
  balance = 1000000
  pnl = 0
  position = 0

  last_signal = 'hold'
  last_price = 0
  c = 0

  trade_date_start = []
  trade_date_end = []
  trade_days = []
  trade_side = []
  trade_pnl = []
  trade_ret = []

  cum_value = []

  for index, row in bt_df.iterrows():
      # check and close any positions
      if row.EXIT_LONG and last_signal == 'long':
        trade_date_end.append(row.name)
        trade_days.append(c)

        pnl = (row.Open - last_price) * position
        trade_pnl.append(pnl)
        trade_ret.append((row.Open / last_price - 1) * 100)
        
        balance = balance + row.Open * position
        
        position = 0
        last_signal = 'hold'

        c = 0
      
      elif row.EXIT_SHORT and last_signal == 'short':
        trade_date_end.append(row.name)
        trade_days.append(c)
        
        pnl = (row.Open - last_price) * position
        trade_pnl.append(pnl)
        trade_ret.append((last_price / row.Open - 1) * 100)

        balance = balance + pnl

        position = 0
        last_signal = 'hold'

        c = 0


      # check signal and enter any possible position
      if row.LONG and last_signal != 'long':
        last_signal = 'long'
        last_price = row.Open
        trade_date_start.append(row.name)
        trade_side.append('long')

        position = int(balance / row.Open)
        cost = position * row.Open
        balance = balance - cost

        c = 0

      elif row.SHORT and last_signal != 'short':
        last_signal = 'short'
        last_price = row.Open
        trade_date_start.append(row.name)
        trade_side.append('short')

        position = int(balance / row.Open) * -1
        
        c = 0
      
      if stop_loss_lvl:
        # check stop loss
        if last_signal == 'long' and (row.Low / last_price - 1) * 100 <= stop_loss_lvl:
          c = c + 1

          trade_date_end.append(row.name)
          trade_days.append(c)

          stop_loss_price = last_price + round(last_price * (stop_loss_lvl / 100), 4)

          pnl = (stop_loss_price - last_price) * position
          trade_pnl.append(pnl)
          trade_ret.append((stop_loss_price / last_price - 1) * 100)
          
          balance = balance + stop_loss_price * position
          
          position = 0
          last_signal = 'hold'

          c = 0

        elif last_signal == 'short' and (last_price / row.Low - 1) * 100 <= stop_loss_lvl:
          c = c + 1

          trade_date_end.append(row.name)
          trade_days.append(c)
          
          stop_loss_price = last_price - round(last_price * (stop_loss_lvl / 100), 4)

          pnl = (stop_loss_price - last_price) * position
          trade_pnl.append(pnl)
          trade_ret.append((last_price / stop_loss_price - 1) * 100)

          balance = balance + pnl

          position = 0
          last_signal = 'hold'

          c = 0

    
      # compute market value and count days for any possible poisition
      if last_signal == 'hold':
        market_value = balance
      elif last_signal == 'long':
        c = c + 1
        market_value = position * row.Close + balance
      else: 
        c = c + 1
        market_value = (row.Close - last_price) * position + balance
      
      cum_value.append(market_value)


  # generate analysis
  # performance over time
  cum_ret_df = pd.DataFrame(cum_value, index=bt_df.index, columns=['CUM_RET'])
  cum_ret_df['CUM_RET'] = (cum_ret_df.CUM_RET / 1000000 - 1) * 100
  cum_ret_df['BUY_HOLD'] = (bt_df.Close / bt_df.Open.iloc[0] - 1) * 100
  cum_ret_df['ZERO'] = 0

  # trade stats
  size = min(len(trade_date_start), len(trade_date_end))

  tarde_dict = {
      'START': trade_date_start[:size],
      'END': trade_date_end[:size],
      'SIDE': trade_side[:size],
      'DAYS': trade_days[:size],
      'PNL': trade_pnl[:size],
      'RET': trade_ret[:size]
  }

  trade_df = pd.DataFrame(tarde_dict)

  num_trades = trade_df.groupby('SIDE').count()[['START']]
  num_trades_win = trade_df[trade_df.PNL > 0].groupby('SIDE').count()[['START']]

  avg_days = trade_df.groupby('SIDE').mean()[['DAYS']]

  avg_ret = trade_df.groupby('SIDE').mean()[['RET']]
  avg_ret_win = trade_df[trade_df.PNL > 0].groupby('SIDE').mean()[['RET']]
  avg_ret_loss = trade_df[trade_df.PNL < 0].groupby('SIDE').mean()[['RET']]

  std_ret = trade_df.groupby('SIDE').std()[['RET']]

  detail_df = pd.concat([
                        num_trades, num_trades_win, avg_days,
                        avg_ret, avg_ret_win, avg_ret_loss, std_ret
                        ], axis=1, sort=False)

  detail_df.columns = [
                      'NUM_TRADES', 'NUM_TRADES_WIN', 'AVG_DAYS', 
                      'AVG_RET', 'AVG_RET_WIN', 'AVG_RET_LOSS', 'STD_RET'
                      ]

  detail_df.round(2)

  # max drawdown
  mv_df = pd.DataFrame(cum_value, index=bt_df.index, columns=['MV'])

  days = len(mv_df)

  roll_max = mv_df.MV.rolling(window=days, min_periods=1).max()
  drawdown_val = mv_df.MV - roll_max
  drawdown_pct = (mv_df.MV / roll_max - 1) * 100

  # return all stats
  return {
      'cum_ret_df': cum_ret_df,
      'max_drawdown': {
          'value': round(drawdown_val.min(), 0), 
          'pct': round(drawdown_pct.min(), 2)
          },
      'trade_stats': detail_df
  }

result = run_stock_ta_backtest(bt_df)

result['cum_ret_df'].plot(figsize=(15, 5))

print('Max Drawdown:', result['max_drawdown']['pct'], '%')

result['trade_stats']

ticker = ticker
start_date = start_date
end_date = end_date

df = get_stock_backtest_data(ticker, start_date, end_date)

bt_df = prepare_stock_ta_backtest_data(
    df, start_date, end_date, 
    strategy_KeltnerChannel_origin, n=10
    )

result = run_stock_ta_backtest(bt_df)

result['cum_ret_df'].plot(figsize=(15, 5))
print('Max Drawdown:', result['max_drawdown']['pct'], '%')
result['trade_stats']

ticker = ticker
start_date = start_date
end_date = end_date

df = get_stock_backtest_data(ticker, start_date, end_date)


n_list = [i for i in range(10, 30, 5)]
stop_loss_lvl = [-i for i in range(2, 5, 1)]
stop_loss_lvl.append(None)

result_dict = {
    'n': [],
    'l': [],
    'return': [],
    'max_drawdown': []
}

for n in n_list:
  for l in stop_loss_lvl:
    bt_df = prepare_stock_ta_backtest_data(
        df, start_date, end_date, 
        strategy_KeltnerChannel_origin, n=n
        )

    result = run_stock_ta_backtest(bt_df, stop_loss_lvl=l)

    result_dict['n'].append(n)
    result_dict['l'].append(l)
    result_dict['return'].append(result['cum_ret_df'].iloc[-1, 0])
    result_dict['max_drawdown'].append(result['max_drawdown']['pct'])


df = pd.DataFrame(result_dict)
print(df.sort_values('return', ascending=False))

from itertools import product

a = [5, 10]
b = [1, 3]
c = [2, 4]

list(product(a, b, c))
param_list = [a, b, c]

list(product(*param_list))

def test_func(**kwargs):
  a = kwargs.get('a', 10)
  b = kwargs.get('b', 2)
  c = kwargs.get('c', 2)

  print(a, b, c)

test_func(a=1, b=2, c=3)

param_dict = {'a': 1, 'b': 2, 'c': 3}

test_func(**param_dict)

param_name = ['a', 'b', 'c']
param = [1, 2, 3]

dict(zip(param_name, param))
dict(zip(['a', 'b', 'c'], [1, 2, 3]))

a = [5, 10]
b = [1, 3]
c = [2, 4]

param_list = [a, b, c]
param_name = ['a', 'b', 'c']
param_dict_list = [dict(zip(param_name, param)) for param in list(product(*param_list))]
param_dict_list

strategies = [
  {
    'func': strategy_KeltnerChannel_origin,
    'param': {
      'n': [i for i in range(10, 35, 5)]
    }
  },

  {
    'func': strategy_BollingerBands,
    'param': {
      'n': [i for i in range(10, 35, 5)],
      'n_rng': [1, 2]
    }
  },

  {
    'func': strategy_MA,
    'param': {
      'n': [i for i in range(10, 110, 10)],
      'ma_type': ['sma', 'ema']
    }
  },

  {
    'func': strategy_MACD,
    'param': {
      'n_slow': [i for i in range(10, 16)],
      'n_fast': [i for i in range(20, 26)],
      'n_sign': [i for i in range(5, 11)]
    }
  },

  {
    'func': strategy_RSI,
    'param': {
      'n': [i for i in range(5, 21)]
    }
  },

  {
    'func': strategy_WR,
    'param': {
      'n': [i for i in range(5, 21)]
    }
  },

  {
    'func': strategy_Stochastic_fast,
    'param': {
      'k': [i for i in range(15, 26)],
      'd': [i for i in range(5, 11)]
    }
  },

  {
    'func': strategy_Stochastic_slow,
    'param': {
      'k': [i for i in range(15, 26)],
      'd': [i for i in range(5, 11)],
      'dd': [i for i in range(1, 6)]
    }
  },

  {
    'func': strategy_Ichmoku,
    'param': {
      'n_conv': [i for i in range(5, 16)],
      'n_base': [i for i in range(20, 36)],
      'n_span_b': [26]
    }
  },
]

for s in strategies:
  func = s['func']
  param = s['param']

  param_name = []
  param_list = []

  for k in param:
    param_name.append(k)
    param_list.append(param[k])

  param_dict_list = [dict(zip(param_name, param)) for param in list(product(*param_list))]
  
  print(len(param_dict_list))
  
ticker = ticker
start_date = start_date
end_date = end_date

df = get_stock_backtest_data(ticker, start_date, end_date)

stop_loss_lvl = [-i for i in range(2, 6, 1)]
stop_loss_lvl.append(None)

result_dict = {
    'strategy': [],
    'param': [],
    'stoploss': [],
    'return': [],
    'max_drawdown': []
}

for s in strategies:
  func = s['func']
  param = s['param']

  strategy_name = str(func).split(' ')[1]

  param_name = []
  param_list = []

  for k in param:
    param_name.append(k)
    param_list.append(param[k])

  param_dict_list = [dict(zip(param_name, param)) for param in list(product(*param_list))]
  total_param_dict = len(param_dict_list)

  c = 0

  for param_dict in param_dict_list:
    clear_output()
    c = c + 1
    print('Running backtest for {} - ({}/{})'.format(strategy_name, c, total_param_dict))

    for l in stop_loss_lvl:
      bt_df = prepare_stock_ta_backtest_data(
          df, start_date, end_date, 
          func, **param_dict)

      result = run_stock_ta_backtest(bt_df, stop_loss_lvl=l)

      result_dict['strategy'].append(strategy_name)
      result_dict['param'].append(str(param_dict))
      result_dict['stoploss'].append(l)
      result_dict['return'].append(result['cum_ret_df'].iloc[-1, 0])
      result_dict['max_drawdown'].append(result['max_drawdown']['pct'])


df = pd.DataFrame(result_dict)
df.to_csv(f'{ticker}_{start_date}_{end_date}_backtest.csv')
print(df.sort_values('return', ascending=True).head(50))
print(df.sort_values('return', ascending=False).head(50))