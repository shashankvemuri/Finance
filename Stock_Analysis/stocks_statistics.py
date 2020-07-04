import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import math
from scipy.stats import norm
import warnings
warnings.filterwarnings("ignore") 
import yfinance as yf
yf.pdr_override()
import datetime as dt
from scipy.stats import shapiro
import scipy as sp
from scipy.stats import anderson
from scipy.stats import pearsonr
from scipy.stats import spearmanr
from scipy.stats import kendalltau
from scipy.stats import ttest_rel
from scipy.stats import boxcox
from scipy.stats import ks_2samp
from scipy.stats import chi2_contingency
from scipy.stats import chi2
from scipy.stats import ttest_ind
from scipy.stats import f_oneway
from scipy.stats import mannwhitneyu
from scipy.stats import wilcoxon
from scipy.stats import kruskal
from scipy.stats import friedmanchisquare
from scipy.stats import levene
from scipy.stats import mood
from scipy.stats import median_test


symbol = 'AAPL'
alpha = 0.05

num_of_years = 5
start = dt.date.today() - dt.timedelta(days=365*num_of_years)
end = dt.date.today()

dataset = yf.download(symbol,start,end)

print("__________________Exploratory Data Analysis__________________")
print("Stock Data")
print('-'*60)
print("Dataset information") 
print(dataset.info(memory_usage='deep',verbose=False))
print('-'*60)
print(dataset.info())
print('-'*60)
print("Data type:")
print(dataset.dtypes)
print('-'*60)
print("Check unique values wihtout NaN")
print(dataset.nunique())
print('-'*60)
print("Data shape:")
print(dataset.shape)
print('-'*60)
print("Data columns Names:")
print(dataset.columns)
print('-'*60)
print("Check for NaNs:")
print(dataset.isnull().values.any())
print('-'*60)
print("Data Statistics Summary:")
print(dataset.describe())

dataset['Log_Returns'] = np.log(dataset['Adj Close'].shift(-1)) - np.log(dataset['Adj Close'])

mu = dataset['Log_Returns'].mean()
sigma = dataset['Log_Returns'].std(ddof=1)

density = pd.DataFrame()
density['x'] = np.arange(dataset['Log_Returns'].min()-0.01, dataset['Log_Returns'].max()+0.01, 0.001)
density['pdf'] = norm.pdf(density['x'], mu, sigma)

dataset['Log_Returns'].hist(bins=50, figsize=(15, 8))
plt.plot(density['x'], density['pdf'], color='red')
plt.show()

dataset['Log_Returns'].plot(figsize=(20, 8))
plt.title("Stock Log Returns")
plt.axhline(0, color='red')
plt.ylabel('Log Returns')
plt.show()

drops = [-0.01, -0.05, -0.10, -0.15, -0.20, -0.25, -0.30, -0.35, -0.40, -0.45, -0.50]
for d in drops:
    prob_returns = norm.cdf(d, mu, sigma)
    print('The Probability of', d, 'is', prob_returns)

prob_return = norm.cdf(-0.03, mu, sigma)
print('The Probability is ', prob_return)

mu225 = 225*mu
sigma225 = (225**0.5) * sigma
print('The probability of dropping over 10% in 225 days is ', norm.cdf(-0.10, mu225, sigma225))

drops = [-0.01, -0.05, -0.10, -0.15, -0.20, -0.25, -0.30, -0.35, -0.40, -0.45, -0.50]
for d in drops:
    prob_returns = norm.cdf(d, mu225, sigma225)
    print('The Probability of dropping over', d,'% in 225 days is', round(prob_returns, 5))

VaR = norm.ppf(0.05, mu, sigma)
print('Stock value at risk ', VaR)

print('5% quantile ', norm.ppf(0.05, mu, sigma))
# 95% quantile
print('95% quantile ', norm.ppf(0.95, mu, sigma))

q25 = norm.ppf(0.25, mu, sigma)
print('25% quantile ', q25)
# 75% quantile
q75 = norm.ppf(0.75, mu, sigma) 
print('75% quantile ', q75)

mu = dataset['Log_Returns'].mean()
sigma = dataset['Log_Returns'].std(ddof=1)
n = dataset['Log_Returns'].shape[0]

zhat = (mu - 0)/(sigma/n**0.5)
print(zhat)

zleft = norm.ppf(alpha/2, 0, 1)
zright = -zleft  # z-distribution is symmetric 
print(zleft, zright)

print('At significant level of {}, shall we reject: {}'.format(alpha, zhat>zright or zhat<zleft))

mu = dataset['Log_Returns'].mean()
sigma = dataset['Log_Returns'].std(ddof=1)
n = dataset['Log_Returns'].shape[0]

zhat = (mu - 0)/(sigma/n**0.5)
print(zhat)
zright = norm.ppf(1-alpha, 0, 1)
print(zright)

print('At significant level of {}, shall we reject: {}'.format(alpha, zhat>zright))

p_value = 1 - norm.cdf(zhat, 0, 1)
print(p_value)

print('At significant level of {}, shall we reject: {}'.format(alpha, p_value < alpha))

W_test, p_value = shapiro(dataset['Log_Returns'])

print('Shapiro-Wilk Test')
print('-'*40)

alpha = 0.05
if p_value < alpha:  # null hypothesis: x comes from a normal distribution
    print("H0: the sample has a Gaussian distribution.")
    print("The null hypothesis can be rejected")
else:
    print("H1: the sample does not have a Gaussian distribution.")
    print("The null hypothesis cannot be rejected")

result = anderson(dataset['Log_Returns'])

print('D’Agostino’s K^2 Test')
print('-'*40)
print('Statistic: %.3f' % result.statistic)
p = 0
for i in range(len(result.critical_values)):
	sl, cv = result.significance_level[i], result.critical_values[i]
	if result.statistic < result.critical_values[i]:
		print('%.3f: %.3f, data looks normal (fail to reject H0)' % (sl, cv))
	else:
		print('%.3f: %.3f, data does not look normal (reject H0)' % (sl, cv))

coef, p_value = pearsonr(dataset['Open'], dataset['Adj Close'])


print('Pearson’s Correlation Coefficient')
print('-'*40)
print('Correlation Test: %.3f' % coef)
# interpret the significance
alpha = 0.05
if p_value > alpha:
	print('H0: the two samples are independent. p=%.3f' % p_value)
else:
	print('H1: there is a dependency between the samples. p=%.3f' % p_value)

coef, p_value = spearmanr(dataset['Open'], dataset['Adj Close'])


print('Spearman’s Rank Correlation')
print('-'*40)
print('Spearmans correlation coefficient: %.3f' % coef)
# interpret the significance
alpha = 0.05
if p_value > alpha:
	print('Samples are uncorrelated (fail to reject H0) p=%.3f' % p_value)
else:
	print('Samples are correlated (reject H0) p=%.3f' % p_value)
coef, p_value = kendalltau(dataset['Open'], dataset['Adj Close'])

print('Kendall’s Rank Correlation')
print('-'*40)
print('Kendall correlation coefficient: %.3f' % coef)
# interpret the significance
alpha = 0.05
if p > alpha:
	print('Samples are uncorrelated (fail to reject H0) p=%.3f' % p_value)
else:
	print('Samples are correlated (reject H0) p=%.3f' % p_value)
stat, p_value, dof, expected = chi2_contingency(dataset[['Open','Low','High','Adj Close','Volume']])


print('Chi-Squared Test')
print('-'*40)


prob = 0.95
critical = chi2.ppf(prob, dof)
if abs(stat) >= critical:
	print('Dependent (reject H0)')
else:
	print('Independent (fail to reject H0)')


alpha = 1.0 - prob
if p_value <= alpha:
	print('Dependent (reject H0)')
else:
	print('Independent (fail to reject H0)')


print('dof=%d' % dof)
print(expected)
# interpret test-statistic
prob = 0.95
critical = chi2.ppf(prob, dof)
print('probability=%.3f, critical=%.3f, stat=%.3f' % (prob, critical, stat))
if abs(stat) >= critical:
	print('Dependent (reject H0)')
else:
	print('Independent (fail to reject H0)')
# interpret p-value
alpha = 1.0 - prob
print('significance=%.3f, p=%.3f' % (alpha, p_value))
if p <= alpha:
	print('Dependent (reject H0)')
else:
	print('Independent (fail to reject H0)')
stat, p_value = ttest_ind(dataset['Open'], dataset['Adj Close'])


print('Paired Students t-Test')
print('-'*40)
print('Statistics=%.3f, p=%.3f' % (stat, p_value))
# interpret
alpha = 0.05
if p_value > alpha:
	print('Same distributions (fail to reject H0)')
else:
	print('Different distributions (reject H0)')

stat, p_value = ttest_rel(dataset['Open'], dataset['Adj Close'])


print('Paired Students t-Test')
print('-'*40)
print('Statistics=%.3f, p=%.3f' % (stat, p))
# interpret
alpha = 0.05
if p_value > alpha:
	print('Same distributions (fail to reject H0)')
else:
	print('Different distributions (reject H0)')
stat, p_value = f_oneway(dataset['Open'], dataset['Adj Close'], dataset['Volume'])


print('Analysis of Variance Test (ANOVA)')
print('-'*40)
print('Statistics=%.3f, p=%.3f' % (stat, p_value))
# interpret
alpha = 0.05
if p_value > alpha:
	print('Same distributions (fail to reject H0)')
else:
	print('Different distributions (reject H0)')
stat, p_value = mannwhitneyu(dataset['Open'], dataset['Adj Close'])


print('Mann-Whitney U Test')
print('-'*40)
print('Statistics=%.3f, p=%.3f' % (stat, p_value))
# interpret
alpha = 0.05
if p_value > alpha:
	print('Same distribution (fail to reject H0)')
else:
	print('Different distribution (reject H0)')
stat, p_value = wilcoxon(dataset['Open'], dataset['Adj Close'])


print('Wilcoxon Signed-Rank Test')
print('-'*40)
print('Statistics=%.3f, p=%.3f' % (stat, p_value))
# interpret
alpha = 0.05
if p_value > alpha:
	print('Same distribution (fail to reject H0)')
else:
	print('Different distribution (reject H0)')
stat, p_value = kruskal(dataset['Open'], dataset['Adj Close'], dataset['Volume'])


print('Kruskal-Wallis Test')
print('-'*40)
print('Statistics=%.3f, p=%.3f' % (stat, p_value))
# interpret
alpha = 0.05
if p_value > alpha:
	print('Same distributions (fail to reject H0)')
else:
	print('Different distributions (reject H0)')
stat, p_value = friedmanchisquare(dataset['Open'], dataset['Adj Close'], dataset['Volume'])


print('Friedman Test')
print('-'*40)
print('Statistics=%.3f, p=%.3f' % (stat, p_value))
# interpret
alpha = 0.05
if p_value > alpha:
	print('Same distributions (fail to reject H0)')
else:
	print('Different distributions (reject H0)')
stat, p_value = levene(dataset['Open'], dataset['Adj Close'])

print('Levene Test')
print('-'*40)
print('Statistics=%.3f, p=%.3f' % (stat, p_value))
# interpret
alpha = 0.05
if p_value > alpha:
	print('Same distributions (fail to reject H0)')
else:
	print('Different distributions (reject H0)')
stat, p_value = mood(dataset['Open'], dataset['Adj Close'])


print('Mood Test')
print('-'*40)
print('Statistics=%.3f, p=%.3f' % (stat, p_value))
# interpret
alpha = 0.05
if p_value > alpha:
	print('Same distributions (fail to reject H0)')
else:
	print('Different distributions (reject H0)')
stat, p_value, med, tbl = median_test(dataset['Open'], dataset['Adj Close'], dataset['Volume'])


print('Mood’s median test')
print('-'*40)
print('Statistics=%.3f, p=%.3f' % (stat, p_value))
# interpret
alpha = 0.05
if p_value > alpha:
	print('Same distributions (fail to reject H0)')
else:
	print('Different distributions (reject H0)')


stat, p_value, med, tbl = median_test(dataset['Open'], dataset['Adj Close'], dataset['Volume'],lambda_="log-likelihood")


print('Mood’s median test with lambda')
print('-'*40)
print('Statistics=%.3f, p=%.3f' % (stat, p_value))
# interpret
alpha = 0.05
if p_value > alpha:
	print('Same distributions (fail to reject H0)')
else:
	print('Different distributions (reject H0)')
stat, p_value = ks_2samp(dataset['Open'], dataset['Adj Close'])


print('Kolmogorov-Smirnov Test')
print('-'*40)
print('Statistics=%.3f, p=%.3f' % (stat, p_value))
# interpret
alpha = 0.05
if p_value > alpha:
	print('Same distributions (fail to reject H0)')
else:
	print('Different distributions (reject H0)')

dataset['boxcox'], lam = boxcox(dataset['Adj Close'])

print('Lambda: %f' % lam)

plt.title('Stock Box-Cox Power Transformation')
plt.plot(dataset['boxcox'])
plt.show()

plt.title('Stock Box-Cox Power Transformation in Histogram')
plt.hist(dataset['boxcox'])
plt.grid()
plt.show()