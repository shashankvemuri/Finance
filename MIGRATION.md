# Finance v2 migration ledger

Legacy baseline: `12dac57c7f62146f7073ccc17f64bc45fd687b5d`. Every Python file is recorded below before deletions.
Status is execution evidence, never an inference of correctness from imports. Pending rows retain their legacy source. Detailed run evidence is in `audit/legacy_runs.json`.

| Old path | Concepts / purpose | Run status | v2 destination | Decision | Reason / replacement | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| `__init__.py` |   init  ; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `find_stocks/IBD_RS_Rating.py` | IBD RS Rating; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `find_stocks/correlated_stocks.py` | correlated stocks; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `find_stocks/finviz_growth_screener.py` | finviz growth screener; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `find_stocks/fundamental_screener.py` | fundamental screener; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `find_stocks/get_rsi_tickers.py` | get rsi tickers; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `find_stocks/green_line_values.py` | green line values; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `find_stocks/minervini_screener.py` | minervini screener; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `find_stocks/price_alert_email.py` | price alert email; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `find_stocks/stock_news_sentiment.py` | stock news sentiment; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `find_stocks/tradingview_signals.py` | tradingview signals; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `find_stocks/twitter_screener.py` | twitter screener; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `find_stocks/yahoo_recommendations.py` | yahoo recommendations; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `machine_learning/arima_time_series.py` | arima time series; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `machine_learning/deep_learning_bot.py` | deep learning bot; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `machine_learning/etf_graphical_lasso.py` | etf graphical lasso; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `machine_learning/kmeans_clustering.py` | kmeans clustering; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `machine_learning/lstm_prediction.py` | lstm prediction; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `machine_learning/ml_models_accuracy.py` | ml models accuracy; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `machine_learning/neural_network_prediction.py` | neural network prediction; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `machine_learning/pca_kmeans_clustering.py` | pca kmeans clustering; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `machine_learning/prophet_price_prediction.py` | prophet price prediction; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `machine_learning/quantitative_indicators_prediction.py` | quantitative indicators prediction; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `machine_learning/sklearn_trading_bot.py` | sklearn trading bot; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `machine_learning/sp500_pca_analysis.py` | sp500 pca analysis; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `machine_learning/stock_probabilistic_analysis.py` | stock probabilistic analysis; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `machine_learning/stock_regression_analysis.py` | stock regression analysis; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `machine_learning/stocker_price_prediction.py` | stocker price prediction; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `machine_learning/technical_indicators_clustering.py` | technical indicators clustering; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `portfolio_strategies/astral_timing_signals.py` | astral timing signals; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `portfolio_strategies/backtest_strategies.py` | backtest strategies; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `portfolio_strategies/backtrader_backtest.py` | backtrader backtest; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `portfolio_strategies/best_moving_averages_analysis.py` | best moving averages analysis; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `portfolio_strategies/ema_crossover_strategy.py` | ema crossover strategy; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `portfolio_strategies/factor_analysis.py` | factor analysis; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `portfolio_strategies/financial_signal_analysis.py` | financial signal analysis; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `portfolio_strategies/geometric_brownian_motion.py` | geometric brownian motion; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `portfolio_strategies/long_hold_stats_analysis.py` | long hold stats analysis; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `portfolio_strategies/ls_dca_analysis.py` | ls dca analysis; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `portfolio_strategies/monte_carlo.py` | monte carlo; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `portfolio_strategies/moving_average_crossover_signals.py` | moving average crossover signals; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `portfolio_strategies/moving_avg_strategy.py` | moving avg strategy; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `portfolio_strategies/optimal_portfolio.py` | optimal portfolio; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `portfolio_strategies/optimized_bollinger_bands.py` | optimized bollinger bands; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `portfolio_strategies/pairs_trading.py` | pairs trading; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `portfolio_strategies/portfolio_analysis.py` | portfolio analysis; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `portfolio_strategies/portfolio_optimization.py` | portfolio optimization; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `portfolio_strategies/portfolio_var_simulation.py` | portfolio var simulation; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `portfolio_strategies/risk_management.py` | risk management; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `portfolio_strategies/robinhood_bot.py` | robinhood bot; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `portfolio_strategies/rsi_trendline_strategy.py` | rsi trendline strategy; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `portfolio_strategies/rwb_strategy.py` | rwb strategy; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `portfolio_strategies/sma_trading_strategy.py` | sma trading strategy; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `portfolio_strategies/stock_spread_plotter.py` | stock spread plotter; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `portfolio_strategies/support_resistance_finder.py` | support resistance finder; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_analysis/backest_all_indicators.py` | backest all indicators; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_analysis/capm_analysis.py` | capm analysis; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_analysis/earnings_call_sentiment_analysis.py` | earnings call sentiment analysis; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_analysis/estimating_returns.py` | estimating returns; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_analysis/intrinsic_value.py` | intrinsic value; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_analysis/kelly_criterion.py` | kelly criterion; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_analysis/ma_backtesting.py` | ma backtesting; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_analysis/ols_regression.py` | ols regression; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_analysis/performance_risk_analysis.py` | performance risk analysis; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_analysis/risk_vs_returns.py` | risk vs returns; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_analysis/seasonal_stock_analysis.py` | seasonal stock analysis; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_analysis/sma_histogram.py` | sma histogram; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_analysis/sp500_cot_sentiment_analysis.py` | sp500 cot sentiment analysis; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_analysis/sp500_valuation.py` | sp500 valuation; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_analysis/stock_pivot_resistance.py` | stock pivot resistance; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_analysis/stock_profit_loss.py` | stock profit loss; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_analysis/stock_returns_statistical_analysis.py` | stock returns statistical analysis; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_analysis/twitter_sentiment_analysis.py` | twitter sentiment analysis; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_analysis/var_analysis.py` | var analysis; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_analysis/view_stock_returns.py` | view stock returns; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_data/autoscraper_finviz_data.py` | autoscraper finviz data; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_data/dividend_history.py` | dividend history; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_data/fibonacci_retracement.py` | fibonacci retracement; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_data/finviz_home_scraper.py` | finviz home scraper; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_data/finviz_insider_trades.py` | finviz insider trades; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_data/finviz_news_scraper.py` | finviz news scraper; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_data/finviz_stock_scraper.py` | finviz stock scraper; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_data/fundamental_ratios.py` | fundamental ratios; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_data/get_dividend_calendar.py` | get dividend calendar; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_data/green_line_test.py` | green line test; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_data/high_dividend_yield.py` | high dividend yield; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_data/historical_sp500_data.py` | historical sp500 data; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_data/main_indicators_one_graph.py` | main indicators one graph; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_data/main_indicators_streamlit.py` | main indicators streamlit; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_data/pivots_calculator.py` | pivots calculator; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_data/reddit_scraper.py` | reddit scraper; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_data/send_top_movers.py` | send top movers; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_data/stock_VWAP.py` | stock VWAP; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_data/stock_data_sms.py` | stock data sms; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_data/stock_earnings.py` | stock earnings; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_data/stock_twilio_server.py` | stock twilio server; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_data/tradingview_intraday_data.py` | tradingview intraday data; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_data/tradingview_recommendations.py` | tradingview recommendations; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `stock_data/yf_intraday_data.py` | yf intraday data; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `ta_functions.py` | ta functions; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/EMA.py` | EMA; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/EMA_volume.py` | EMA volume; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/EWMA.py` | EWMA; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/EWMA_Double.py` | EWMA Double; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/EWMA_Triple.py` | EWMA Triple; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/GANN_lines_angles.py` | GANN lines angles; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/GMMA.py` | GMMA; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/MACD.py` | MACD; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/MA_high_low.py` | MA high low; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/MFI.py` | MFI; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/PVI.py` | PVI; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/PVT.py` | PVT; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/ROC.py` | ROC; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/ROI.py` | ROI; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/RSI.py` | RSI; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/RSI_BollingerBands.py` | RSI BollingerBands; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/SMA.py` | SMA; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/TRIMA.py` | TRIMA; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/TWAP.py` | TWAP; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/VWAP.py` | VWAP; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/WMA.py` | WMA; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/WSMA.py` | WSMA; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/Z_Score_Indicator.py` | Z Score Indicator; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/absolute_price_oscillator.py` | absolute price oscillator; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/acceleration_bands.py` | acceleration bands; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/accum_dist_line.py` | accum dist line; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/aroon.py` | aroon; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/aroon_oscillator.py` | aroon oscillator; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/avg_directional_index.py` | avg directional index; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/avg_true_range.py` | avg true range; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/balance_of_power.py` | balance of power; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/beta_indicator.py` | beta indicator; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/bollinger_bands.py` | bollinger bands; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/bollinger_bandwidth.py` | bollinger bandwidth; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/breadth_indicator.py` | breadth indicator; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/candle_abs_returns.py` | candle abs returns; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/central_pivot_range_cpr.py` | central pivot range cpr; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/chaikin_money_flow.py` | chaikin money flow; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/chaikin_oscillator.py` | chaikin oscillator; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/commodity_channel_index.py` | commodity channel index; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/correlation_coeff.py` | correlation coeff; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/covariance.py` | covariance; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/detrended_price_oscillator.py` | detrended price oscillator; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/donchain_channel.py` | donchain channel; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/double_exp_moving_avg.py` | double exp moving avg; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/dynamic_momentum_index.py` | dynamic momentum index; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/ease_of_movement.py` | ease of movement; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/force_index.py` | force index; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/geometric_return_indicator.py` | geometric return indicator; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/golden_death_cross.py` | golden death cross; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/high_minus_low.py` | high minus low; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/hull_moving_average.py` | hull moving average; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/keltners_channels.py` | keltners channels; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/linear_regression.py` | linear regression; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/linear_regression_slope.py` | linear regression slope; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/linear_weighted_moving_average.py` | linear weighted moving average; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/mcclellan_oscillator.py` | mcclellan oscillator; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/momentum.py` | momentum; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/moving_average_envelopes.py` | moving average envelopes; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/moving_average_high_low.py` | moving average high low; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/moving_average_ribbon.py` | moving average ribbon; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/moving_avg_env.py` | moving avg env; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/moving_linear_regression.py` | moving linear regression; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/new_highs_new_lows.py` | new highs new lows; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/pivot_point.py` | pivot point; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/price_channels.py` | price channels; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/price_relative.py` | price relative; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/realised_volatility.py` | realised volatility; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/relative_volatility_index.py` | relative volatility index; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/smoothed_moving_average.py` | smoothed moving average; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/speed_resistance_lines.py` | speed resistance lines; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/standard_deviation_volatility.py` | standard deviation volatility; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/stochastic_RSI.py` | stochastic RSI; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/stochastic_fast.py` | stochastic fast; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/stochastic_full.py` | stochastic full; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/stochastic_slow.py` | stochastic slow; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/super_trend.py` | super trend; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/true_strength_index.py` | true strength index; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/ultimate_oscillator.py` | ultimate oscillator; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/variance_indicator.py` | variance indicator; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/volume_price_confirmation_Indicator.py` | volume price confirmation Indicator; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `technical_indicators/volume_weighted_moving_average.py` | volume weighted moving average; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
| `tickers.py` | tickers; source review pending | Pending isolated execution | Pending | Pending | Preserve until reviewed | Pending |
