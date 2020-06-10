# # Factor Analysis Portfolio

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import math
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
yf.pdr_override()
import datetime as dt
from dateutil import relativedelta


# input
symbols = ['AAPL','MSFT','AMD','NVDA']
start = '2012-01-01'
end = '2019-09-11'

df = pd.DataFrame()
for s in symbols:
    df[s] = yf.download(s,start,end)['Adj Close']

df.head()

df.tail()

from factor_analyzer import FactorAnalyzer

fa = FactorAnalyzer(rotation=None)

fa.fit(df)

fa.get_communalities()

ev, v = fa.get_eigenvalues()
ev

plt.scatter(range(1,df.shape[1]+1),ev)
plt.plot(range(1,df.shape[1]+1),ev)
plt.title('Factor Analysis')
plt.xlabel('Factors')
plt.ylabel('Eigenvalue')
plt.grid()
plt.show()

from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity
chi_square_value,p_value=calculate_bartlett_sphericity(df)
chi_square_value, p_value

from factor_analyzer.factor_analyzer import calculate_kmo
kmo_all,kmo_model=calculate_kmo(df)

kmo_model


from factor_analyzer import (ConfirmatoryFactorAnalyzer,              ModelSpecificationParser)

model_spec = ModelSpecificationParser.parse_model_specification_from_dict(df)

cfa = ConfirmatoryFactorAnalyzer(model_spec, disp=False)

cfa.fit(df.values)

cfa.loadings_

cfa.factor_varcovs_

cfa.transform(df.values)

