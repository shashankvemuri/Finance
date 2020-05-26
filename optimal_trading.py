import sys
import operator
import numpy as np
import pandas as pd
from pandas_datareader import DataReader
import datetime

stock = 'XRF'
start_date = datetime.datetime.now() - datetime.timedelta(days=7)
end_date = datetime.date.today() 

def find_optimal_action(priceVec, transFeeRate, use_DP=True):
	
	_BUY = 1
	_HOLD = 0
	_SELL = -1

	dataLen = len(priceVec)
	actionVec = np.zeros(dataLen)

	# Dynamic Programming method
	if use_DP:
		capital = 1
		money = [{'money' : 0, 'from' : 0 } for _ in range(dataLen)]
		stock = [{'stock' : 0, 'from' : 1 } for _ in range(dataLen)]

		# DP initialization
		money[0]['money'] = capital
		stock[0]['stock'] = capital * (1 - transFeeRate) / priceVec[0]

		# DP recursion
		for t in range(1, dataLen):
			
			# find optimal for sell at time t:
			hold = money[t - 1]['money']
			sell = stock[t - 1]['stock'] * priceVec[t] * (1 - transFeeRate)

			if hold > sell:
				money[t]['money'] = hold
				money[t]['from'] = 0
			else:
				money[t]['money'] = sell
				money[t]['from'] = 1

			# find optimal for buy at time t:
			hold = stock[t - 1]['stock']
			buy = money[t - 1]['money'] * (1 - transFeeRate) / priceVec[t]

			if hold > buy:
				stock[t]['stock'] = hold
				stock[t]['from'] = 1
			else:
				stock[t]['stock'] = buy
				stock[t]['from'] = 0

		# must sell at T
		prev = 0
		actionVec[-1] = _SELL

		# DP trace back
		record = [money, stock]
		for t in reversed(range(1, dataLen)):
			prev = record[prev][t]['from']
			actionVec[t - 1] = _SELL if prev == 0 else _BUY
		
		# Action smoothing
		prevAction = actionVec[0]
		for t in range(1, dataLen):
			if actionVec[t] == prevAction:
				actionVec[t] = _HOLD
			elif actionVec[t] == -prevAction:
				prevAction = actionVec[t]

		return actionVec

	# Baseline method
	else:
		conCount = 3
		for ic in range(dataLen):
			if ic + conCount + 1 > dataLen:
				continue
			if all(x > 0 for x in list(map(operator.sub,priceVec[ic+1:ic+1+conCount], priceVec[ic:ic+conCount]))):
				actionVec[ic] = _BUY
			if all(x < 0 for x in list(map(operator.sub,priceVec[ic+1:ic+1+conCount], priceVec[ic:ic+conCount]))):
				actionVec[ic] = _SELL
		prevAction = _SELL

		for ic in range(dataLen):
			if actionVec[ic] == prevAction:
				actionVec[ic] = _HOLD
			elif actionVec[ic] == -prevAction:
				prevAction = actionVec[ic]
		return actionVec


def profit_estimate(priceVec, transFeeRate, actionVec):

	capital = 1
	capitalOrig = capital
	dataCount = len(priceVec)
	suggestedAction = actionVec
	
	stockHolding = np.zeros((dataCount))
	total = np.zeros((dataCount))
	
	total[0] = capital

	for ic in range(dataCount):
		currPrice = priceVec[ic]
		if ic > 0:
			stockHolding[ic] = stockHolding[ic-1]
		if suggestedAction[ic] == 1:
			if stockHolding[ic] == 0:            
				stockHolding[ic] = capital * (1 - transFeeRate) / currPrice
				capital = 0

		elif suggestedAction[ic] == -1:
			if stockHolding[ic] > 0:
				capital = stockHolding[ic] * currPrice * (1 - transFeeRate)
				stockHolding[ic] = 0

		elif suggestedAction[ic] == 0:
			pass
		else:
			assert False
		total[ic] = capital + stockHolding[ic] * currPrice * (1 - transFeeRate)
	returnRate = (total[-1] - capitalOrig) / capitalOrig
	return returnRate


if __name__ == '__main__':

	SEARCH = False

	df = DataReader(stock, 'yahoo', start_date, end_date)
	transFeeRate = float(0.01)

	priceVec = df["Adj Close"].values
	print('Optimizing over %i numbers of transactions.' % (len(priceVec)))

	actionVec = find_optimal_action(priceVec, transFeeRate)
	returnRate = profit_estimate(priceVec, transFeeRate, actionVec)
	print('Return rate: ', returnRate)
