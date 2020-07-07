import pandas as pd
import numpy as np
import datetime
import quandl
import pandas_datareader as dr
import matplotlib.pyplot as plt
from config import quandl_api

quandl.ApiConfig.api_key = quandl_api()

jan2020 = dr.data.get_data_yahoo('^GSPC', start='2020-01-01', end = '2020-1-31')

sp = quandl.get("YALE/SPCOMP", authtoken=quandl.ApiConfig.api_key, collapse="daily")
sp.reset_index(inplace = True)
print(sp.tail(12))

sp['spreturn'] = sp['S&P Composite'].pct_change()
sp.rename(columns={"Year": "date"}, inplace = True)

print(sp['spreturn'].head())
sp['sign'] = np.sign(sp['spreturn'])
#sp[sp['spreturn'] > 0] = 'pos'
#sp[sp['spreturn'] > 0] = 'neg'
print(sp.head())

totalyr = sp['date'].nunique()
print(totalyr)

def successrate(df,m):
    df['date']= pd.to_datetime(df['date'],format='%m/%d/%Y')
    df['month']= pd.DatetimeIndex(df['date']).month
    df['year']= pd.DatetimeIndex(df['date']).year
    totalyr = df['year'].nunique()
    
    mon=[m,12.0]
    df_mon = df.groupby(df['month']).filter(lambda g: g['month'].isin(mon).all())
    
    sign = ['1']
    totalpos = df_mon.groupby('year').filter(lambda g: g['sign'].isin(sign).all())['year'].nunique()
    sucess_rate = totalpos/totalyr
    
    return sucess_rate,totalpos

jan_sucess_rate,jan_totalpos = successrate(sp,1)

restofyr = sp[(sp['month'] == 1) | (sp['month'] == 12)]
restofyr['FebDecreturn'] = restofyr['S&P Composite'].pct_change()

restofyr['FebDecreturn'] = restofyr['S&P Composite'].pct_change()

restofyr_rtn = restofyr[(restofyr['month'] == 12)][['date','FebDecreturn','year']]
jan_sprtn = sp[sp['month'] == 1][['year','spreturn']]
sp2 = jan_sprtn.merge(restofyr_rtn)
sp2['jan_sign'] = np.sign(sp2['spreturn'])
sp2['FebDec_sign'] = np.sign(sp2['FebDecreturn'])

jan_sprtn = sp[sp['month'] == 1][['year','spreturn']]
sp2 = jan_sprtn.merge(restofyr_rtn)

sp2['jan_sign'] = np.sign(sp2['spreturn'])
sp2['FebDec_sign'] = np.sign(sp2['FebDecreturn'])

sp2[(sp2['jan_sign'] == 1)].year.count()
sp2[(sp2['jan_sign'] == 1) & (sp2['FebDec_sign'] == 1)].year.count()
sp2[(sp2['jan_sign'] == -1) & (sp2['FebDec_sign'] == -1)].year.count()
sp2[sp2['jan_sign'] == sp2['FebDec_sign']].year.count()
sp2[(sp2['jan_sign'] == 1) & (sp2['FebDec_sign'] == 1)].year.count()
sp2[(sp2['jan_sign'] == -1) & (sp2['FebDec_sign'] == -1)].year.count()
sp_corr = sp2[sp2['jan_sign'] == sp2['FebDec_sign']].FebDecreturn.count()
sp2.set_index('year',inplace = True)

sp3 = sp2[sp2['jan_sign'] == sp2['FebDec_sign']][['spreturn','FebDecreturn']]
sp3 = sp2[sp2['jan_sign'] == sp2['FebDec_sign']][['spreturn','FebDecreturn']]
width = 0.75  # the width of the bars

fig, ax = plt.subplots(figsize=(40,20))
rects1 = ax.bar(sp3.index - width/2, sp3['spreturn'], width, label='Jan Return')
rects2 = ax.bar(sp3.index + width/2, sp3['FebDecreturn'], width, label='Feb-Dec Return')
ax.set_ylabel('Return', fontsize=40)
ax.set_xlabel('Year', fontsize=40)
ax.set_title("Jan Barometer on SP500",fontsize=40)
ax.legend(fontsize=40)
ax.tick_params(axis='both', which='major', labelsize=40)
plt.show()

sp2[(sp2['jan_sign'] != sp2['FebDec_sign'])][['spreturn','FebDecreturn']].count()
sp4 = sp2[(sp2['jan_sign'] != sp2['FebDec_sign']) & (sp2['jan_sign'] != 0)][['spreturn','FebDecreturn']]
sp4 = sp4.iloc[1:,:]
width = 0.95  # the width of the bars

fig, ax = plt.subplots(figsize=(40,20))
rects1 = ax.bar(sp4.index - width/2, sp4['spreturn'], width, label='Jan Return')
rects2 = ax.bar(sp4.index + width/2, sp4['FebDecreturn'], width, label='Feb-Dec Return')
ax.set_ylabel('Return',fontsize=40)
ax.set_xlabel('year',fontsize=40)
ax.set_title("Jan Barometer on SP500 - False Predictors",fontsize=40)
ax.legend(fontsize=40)
ax.tick_params(axis='both', which='major', labelsize=40)
plt.show()

sp4['FebDecreturn'].nlargest(5)
sp4['FebDecreturn'].nsmallest(5)
totalyr = sp['year'].nunique()
sp[(sp['month'] == 1) & sp['sign'] == 1].count()

first_sp = sp['S&P Composite'].iloc[11]
last_sp = sp['S&P Composite'].iloc[-1]
sp_tot_yrs= sp['year'].nunique()-1
sp_tot_rtn = (last_sp-first_sp) / first_sp
sp_fullyInvested = ((1+sp_tot_rtn)**(1/sp_tot_yrs)) - 1
sp_pos = sp2[(sp2['jan_sign'] == 1)]
sp_posYr = sp2[(sp2['jan_sign'] == 1)].FebDecreturn.count()

sp_pos['rnt1']= sp_pos['FebDecreturn']+1
sp_sum = sp_pos['rnt1'].sum()
sp_gm = (sp_sum ** (1/sp_posYr) ) - 1

sp_gm = (sp_sum ** (1/sp_posYr) ) - 1

df = dr.data.get_data_yahoo('^IXIC', start='1971-12-31', end = '2019-12-31')
df.reset_index(inplace = True)
df['month'] = pd.DatetimeIndex(df['Date']).month
df['year'] = pd.DatetimeIndex(df['Date']).year
df =df.groupby(['year', 'month']).last().reset_index()
df['nasreturn'] = df['Close'].pct_change()
print (df)

tot_yrs= df['year'].nunique()-1
first = df['Close'][0]
last = df['Close'].iloc[-1]
tot_rtn = (last-first) / first

nas_fullyInvested = ((1+tot_rtn)**(1/tot_yrs)) - 1

nas_restofyr = df[(df['month'] == 1) | (df['month'] == 12)]
nas_restofyr['FebDecreturn'] = nas_restofyr['Close'].pct_change()

restofyr_rtn = nas_restofyr[(nas_restofyr['month'] == 12)][['Date','FebDecreturn','year']]
jan_nasrtn = df[df['month'] == 1][['year','nasreturn']]
nas2 = jan_nasrtn.merge(restofyr_rtn)
nas2['jan_sign'] = np.sign(nas2['nasreturn'])
nas2['FebDec_sign'] = np.sign(nas2['FebDecreturn'])

nas_corr = nas2[(nas2['jan_sign'] == nas2['FebDec_sign'])].FebDecreturn.count()
nas2[(nas2['jan_sign'] == 1)].count()

a = nas2[(nas2['jan_sign'] == 1)]
a['rnt1']= a['FebDecreturn']+1
sum1 = a['rnt1'].sum()
nas_gm = (sum1 ** (1/31) ) - 1

nas2[(nas2['jan_sign'] == 1)].year.count()
nas2[(nas2['jan_sign'] == 1) & (nas2['FebDec_sign'] == 1)].year.count()
nas2[(nas2['jan_sign'] == -1) & (nas2['FebDec_sign'] == -1)].year.count()
worked = nas2[nas2['jan_sign'] == nas2['FebDec_sign']].year.count()

nasYr2Invest = nas2[(nas2['jan_sign'] == 1) & (nas2['FebDec_sign'] == 1)].index.to_list()
total = nas2['year'].count()

nas2.set_index('year', inplace=True)
nas3 = nas2[nas2['jan_sign'] == nas2['FebDec_sign']][['nasreturn','FebDecreturn']]
width = 0.75  # the width of the bars

fig, ax = plt.subplots(figsize=(20,10))
rects1 = ax.bar(nas3.index - width/2, nas3['nasreturn'], width, label='Jan Return')
rects2 = ax.bar(nas3.index + width/2, nas3['FebDecreturn'], width, label='Feb-Dec Return')
ax.set_ylabel('Return')
ax.set_title("Jan Barometer on SP500 - Correct Predictions")
ax.legend()
plt.show()

nas4 = nas2[nas2['jan_sign'] != nas2['FebDec_sign']][['nasreturn','FebDecreturn']]
width = 0.75  # the width of the bars

fig, ax = plt.subplots(figsize=(20,10))
rects1 = ax.bar(nas4.index - width/2, nas4['nasreturn'], width, label='Jan Return')
rects2 = ax.bar(nas4.index + width/2, nas4['FebDecreturn'], width, label='Feb-Dec Return')
ax.set_ylabel('Return')
ax.set_title("Jan Barometer on SP500 - False Predictions")
ax.legend()
plt.subplots()

dji = dr.data.get_data_yahoo('^DJI', start='1984-12-31', end = '2019-12-31')

dji.reset_index(inplace = True)
dji['month'] = pd.DatetimeIndex(dji['Date']).month
dji['year'] = pd.DatetimeIndex(dji['Date']).year
df_dji = dji.groupby(['year', 'month']).last().reset_index()
df_dji['return'] = df_dji['Close'].pct_change()
df_dji['sign'] = np.sign(df_dji['return'])

dow_restofyr = df_dji[(df_dji['month'] == 1) | (df_dji['month'] == 12)]
dow_restofyr['FebDecreturn'] = dow_restofyr['Close'].pct_change()

dow_restofyr_rtn = dow_restofyr[(dow_restofyr['month'] == 12)][['Date','FebDecreturn','year']]
jan_dowrtn = df_dji[df_dji['month'] == 1][['year','return']]
dow2 = jan_dowrtn.merge(dow_restofyr_rtn)
dow2['jan_sign'] = np.sign(dow2['return'])
dow2['FebDec_sign'] = np.sign(dow2['FebDecreturn'])

dow_tot_yrs= dow2['year'].nunique()-1

dow_first = dji['Close'].iloc[0]
dow_last = dji['Close'].iloc[-1]

dow_tot_rtn = (dow_last-dow_first) / dow_first
dow_tot_yr = dji['year'].nunique() -1

dow_fullyInvested = ((1+dow_tot_rtn)**(1/dow_tot_yr)) - 1
dow_corr = dow2[(dow2['jan_sign'] ==dow2['FebDec_sign'])].year.count()
dow_posyr = dow2[(dow2['jan_sign'] == 1) ].year.count()
dow_pos = dow2[(dow2['jan_sign'] == 1)]

dow_pos['rnt1']= dow_pos['FebDecreturn']+1

dow_sum = dow_pos['rnt1'].sum()
dow_gm = (dow_sum ** (1/dow_posyr) ) - 1
print (dow_gm, dow_sum, dow_pos, dow_posyr, dow_tot_yr)


rut = dr.data.get_data_yahoo('^RUT', start='1987-12-31', end = '2019-12-31')
print(rut)

rut.reset_index(inplace = True)
rut['month'] = pd.DatetimeIndex(rut['Date']).month
rut['year'] = pd.DatetimeIndex(rut['Date']).year
df_rut = rut.groupby(['year', 'month']).last().reset_index()
df_rut['return'] = df_rut['Close'].pct_change()
df_rut['sign'] = np.sign(df_rut['return'])

print(df_rut)

rut_restofyr = df_rut[(df_rut['month'] == 1) | (df_rut['month'] == 12)]
rut_restofyr['FebDecreturn'] = rut_restofyr['Close'].pct_change()

rut_restofyr_rtn = rut_restofyr[(rut_restofyr['month'] == 12)][['Date','FebDecreturn','year']]
jan_rutrtn = df_rut[df_rut['month'] == 1][['year','return']]
rut2 = jan_rutrtn.merge(rut_restofyr_rtn)
rut2['jan_sign'] = np.sign(rut2['return'])
rut2['FebDec_sign'] = np.sign(rut2['FebDecreturn'])

rut_first = rut['Close'].iloc[0]
rut_last = rut['Close'].iloc[-1]
rut_tot_rnt = ((rut_last-rut_first)/ rut_first) 
rut_tot_yr = df_rut.year.nunique()

rut_fullyInvested = ((1+rut_tot_rnt)**(1/rut_tot_yr)) - 1
rut_corr = rut2[(rut2['jan_sign'] == rut2['FebDec_sign'])].year.count()

rut_posyr = rut2[(rut2['jan_sign'] == 1)].year.count()
rut_pos = rut2[(rut2['jan_sign'] == 1)]

rut_pos['rnt1'] = rut_pos['FebDecreturn'] +1 
rut_sum = rut_pos['rnt1'].sum()
rut_gm = (rut_sum ** (1/rut_posyr) ) - 1

rut_sum = rut_pos['rnt1'].sum()
print(rut_sum)

rut_gm = (rut_sum ** (1/rut_posyr) ) - 1
print(rut_gm)

index = pd.DataFrame(data = {'index': ['SP500','NASDAQ', 'DOW JONES', 'RUSSEL 2000'],
                            'TotalYears':[sp_tot_yrs,tot_yrs,dow_tot_yr,rut_tot_yr],
                            'Correctly Predicted Years': [sp_corr,nas_corr,dow_corr,rut_corr],
                             'Total_Return': [sp_fullyInvested,nas_fullyInvested,dow_fullyInvested,rut_fullyInvested],
                             'Barometer_Return': [sp_gm,nas_gm,dow_gm,rut_gm]
                            
                            })

index['Success_Rate'] = index['Correctly Predicted Years']/index['TotalYears']
index.style.format({'Total_Return': "{:.2%}",'Barometer_Return': "{:.2%}",'Success_Rate': "{:.2%}"})

index.set_index('index')[['Total_Return','Barometer_Return']].plot(figsize=(20, 8), linewidth=2.5,marker='o', markerfacecolor='black')
plt.ylabel("Return",fontsize=20)
plt.xlabel("index",fontsize=20)
plt.title("Following the Barometer or Ignoring It - Annualized Returns by Index", y=1.02, fontsize=30);
#df.plot(style='.-')
plt.legend(fontsize=20)
plt.tick_params(axis='both', which='major', labelsize=20)
plt.show()

tech = dr.data.get_data_yahoo('XLK', start='1998-12-31', end = '2019-12-31')
consumer_dis = dr.data.get_data_yahoo('XLY', start='1998-12-31', end = '2019-12-31')
healthcare = dr.data.get_data_yahoo('XLV', start='1998-12-31', end = '2019-12-31')
utilities = dr.data.get_data_yahoo('XLU', start='1998-12-31', end = '2019-12-31')
consumer_staples = dr.data.get_data_yahoo('XLP', start='1998-12-31', end = '2019-12-31')
#reits = dr.data.get_data_yahoo('XLRE', start='1998-12-31', end = '2019-12-31') #only till 2015
industrials = dr.data.get_data_yahoo('XLI', start='1998-12-31', end = '2019-12-31')
financials = dr.data.get_data_yahoo('XLF', start='1998-12-31', end = '2019-12-31')
#media = dr.data.get_data_yahoo('XLC', start='1998-12-31', end = '2019-12-31') #only till 2018
materials = dr.data.get_data_yahoo('XLB', start='1998-12-31', end = '2019-12-31')
energy = dr.data.get_data_yahoo('XLE', start='1998-12-31', end = '2019-12-31')

def sector_rate(df):
    df.reset_index(inplace = True)
    df['month'] = pd.DatetimeIndex(df['Date']).month
    df['year'] = pd.DatetimeIndex(df['Date']).year
    df_2 = df.groupby(['year', 'month']).last().reset_index()
    df_2['return'] = df_2['Close'].pct_change()
    df_2['sign'] = np.sign(df_2['return'])
    
    df_restofyr = df_2[(df_2['month'] == 1) | (df_2['month'] == 12)]
    df_restofyr['FebDecreturn'] = df_restofyr['Close'].pct_change()
    df_restofyr_rtn = df_restofyr[(df_restofyr['month'] == 12)][['Date','FebDecreturn','year']]
    jan_dfrtn = df_2[df_2['month'] == 1][['year','return']]
    df2 = jan_dfrtn.merge(df_restofyr_rtn)
    df2['jan_sign'] = np.sign(df2['return'])
    df2['FebDec_sign'] = np.sign(df2['FebDecreturn'])
    
    totalyr = df_2['year'].nunique() -1
    
    df_corr = df2[(df2['jan_sign'] == df2['FebDec_sign'])].year.count()
    df_tp = df2[(df2['jan_sign'] == 1) & (df2['FebDec_sign'] == 1)].year.count()
    df_fp = df2[(df2['jan_sign'] == 1) & (df2['FebDec_sign'] == -1)].year.count()
    df_fn = df2[(df2['jan_sign'] == -1) & (df2['FebDec_sign'] == 1)].year.count()
    df_tn = df2[(df2['jan_sign'] == -1) & (df2['FebDec_sign'] == -1)].year.count()
    
    sucess_rate = df_corr/totalyr
    
    df_first = df['Close'].iloc[0]
    df_last = df['Close'].iloc[-1]
    df_tot_rnt = ((df_last-df_first)/ df_first) -1
    #df_tot_rnt
    df_fullyInvested = ((1+df_tot_rnt)**(1/totalyr)) - 1
    
    df_posyr = df2[(df2['jan_sign'] == 1)].year.count()
 
    df_pos = df2[(df2['jan_sign'] == 1)]
    df_pos['rnt1'] = df_pos['FebDecreturn'] +1 
    df_sum = df_pos['rnt1'].sum()
    #df_gm = (df_sum ** (1/df_posyr) ) - 1
    df_gm = df_pos['FebDecreturn'].mean()
    
    return sucess_rate,df_corr,df_fullyInvested,df_gm,df_tp,df_fp,df_fn,df_tn

sector = [tech,consumer_dis,healthcare, utilities, consumer_staples,industrials, financials,materials,energy]
df_sector = pd.DataFrame({'Sector': ['tech','consumer_dis','healthcare', 'utilities', 'consumer_staples','industrials', 'financials','materials','energy']      
                            })
print(df_sector)

sucess_rate_lst = []
df_corr_lst = []
df_fullyInvested_lst = []
df_gm_lst = []
df_tp_lst = []
df_fp_lst = []
df_fn_lst = []
df_tn_lst = []

for s in sector:
    #print(s)
    sucess_rate,df_corr,df_fullyInvested,df_gm,df_tp,df_fp,df_fn,df_tn = sector_rate(s)
    #print(sucess_rate)
    sucess_rate_lst.append(sucess_rate)
    df_corr_lst.append(df_corr)
    df_fullyInvested_lst.append(df_fullyInvested)
    df_gm_lst.append(df_gm)
    df_tp_lst.append(df_tp)
    df_fp_lst.append(df_fp)
    df_fn_lst.append(df_fn)
    df_tn_lst.append(df_tn)

df_sector['success_rate'] = sucess_rate_lst
df_sector['Correctly Predicted Years'] = df_corr_lst 
df_sector['Ignore Jan Bar Return'] = df_fullyInvested_lst 
df_sector['Jan Bar Return'] = df_gm_lst 
df_sector['True Positives'] = df_tp_lst 
df_sector['False Positives'] = df_fp_lst 
df_sector['False Negatives'] = df_fn_lst 
df_sector['True Negatives'] = df_tn_lst 

df_sector[['Sector','success_rate','Correctly Predicted Years']].style.highlight_max(color='lightgreen').highlight_min(color='#cd4f39').format({'success_rate': "{:.2%}"})
df_sector[['Sector','Ignore Jan Bar Return','Jan Bar Return']].style.highlight_max(color='lightgreen').highlight_min(color='#cd4f39').format({'Ignore Jan Bar Return': "{:.2%}",'Jan Bar Return': "{:.2%}"})
print(df_sector)

df_sector.set_index('Sector')[['Ignore Jan Bar Return','Jan Bar Return']].plot(figsize=(12, 5), linewidth=2.5,marker='o', markerfacecolor='black')
plt.ylabel("Return")
plt.title("Following the Barometer or Ignoring It - Annualized Returns by Sector", y=1.02, fontsize=22);
#df.plot(style='.-')
plt.show()

n_groups = 9
fig, ax = plt.subplots(figsize=(20,10))
index = np.arange(n_groups)
bar_width = 0.35
opacity = 0.8

rects1 = plt.bar(index, df_sector['Jan Bar Return'], bar_width,
alpha=opacity,
color='m',
label='Barometer Return')

rects2 = plt.bar(index + bar_width, df_sector['Ignore Jan Bar Return'], bar_width,
alpha=opacity,
color='y',
label='Ignore Barometer Return')

plt.ylabel('Returns', fontsize=16)
plt.title('Following the Barometer or Ignoring It - Annualized Returns by Sector',fontsize=18)
plt.xticks(index + bar_width, df_sector['Sector'], size=14)
plt.legend(fontsize=18)
plt.show()

def autolabel(rects):
    for rect in rects:
        height = np.round(rect.get_height(),decimals=3)
        ax.annotate('{:.2%}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 6),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=14)

autolabel(rects1)
autolabel(rects2)
plt.tick_params(axis='both', which='major', labelsize=15)
vals = ax.get_yticks()
ax.set_yticklabels(['{:,.1%}'.format(x) for x in vals])
plt.show()

fig, ax1 = plt.subplots(figsize=(15, 5))
df_sector.set_index('Sector')['Correctly Predicted Years'].plot(kind='bar', color='y')
df_sector.set_index('Sector')['sucess_rate'].plot(kind='line', marker='d', secondary_y=True)
ax1.set_ylabel("Correctly Predicted Years")
plt.show()

fig, ax1 = plt.subplots(figsize=(15, 5))
plt.style.use('seaborn-white')
ax2 = ax1.twinx()
chart = df_sector.set_index('Sector')['Correctly Predicted Years'].plot(kind='bar',color = 'y', ax=ax1)
df_sector.set_index('Sector')['sucess_rate'].plot(kind='line', marker='d', ax=ax2)
plt.show()

ax1.set_ylabel("Correctly Predicted # of Years",fontsize=14)
ax2.set_ylabel("Success rate",fontsize=14)
ax1.set_ylim([0,16])
chart.set_xticklabels(chart.get_xticklabels(), rotation=45,fontsize=16)
ax2.legend(loc=9, bbox_to_anchor=(1, -0.2),fontsize=14)
ax1.legend(loc=9, bbox_to_anchor=(1, -0.3),fontsize=14)
plt.title("Jan Barometer Success Rate by Sectors", y=1.02, fontsize=20)
plt.tick_params(axis='both', which='major', labelsize=12)
ax1.tick_params(axis='both', which='major', labelsize=12)
plt.show()

error = df_sector[['Sector', 'True Positives', 'False Positives','False Negatives','True Negatives']]
error.set_index('Sector', inplace=True)

chart2 = error.plot.bar(stacked=True,figsize=(15, 5))
chart2.set_xticklabels(chart.get_xticklabels(), rotation=45,size=14)
chart2.legend(loc=9, bbox_to_anchor=(1.1, 1),fontsize=14)
plt.title("Confusion Matrix by Sector", y=1.02, fontsize=22);

for p in chart2.patches:
    width, height = p.get_width(), p.get_height()
    x, y = p.get_xy() 
    
    chart2.text(x+width/2, 
            y+height/2, 
            height, 
            horizontalalignment='center', 
            verticalalignment='center', fontsize=13)
chart2.set_ylabel("# of Years", fontsize=14)
plt.tick_params(axis='both', which='major', labelsize=14)
plt.subplots()
plt.show()

error['TP + TN'] = error['True Positives'] + error['True Negatives'] 
error['FP + FN'] = error['False Positives'] + error['False Negatives']
error[[ 'TP + TN', 'FP + FN']]

print(sp2)

epidemics = [1889,1916,1918,1957,1981,2009,2014,2015]
epidemic_df = sp2[sp2['year'].isin(epidemics)]
epidemic_df.rename(columns={"spreturn": "JanReturn", 'FebDecreturn': 'FebDecReturn'}, inplace=True)
epidemic_df.round({'JanReturn': 3, 'FebDecReturn': 3})
epidemic_df.style.format({'JanReturn': "{:.2%}",'FebDecReturn': "{:.2%}"})
epidemic_df['Epidemic/Pandemic'] = ['Influenza Pandemic','American Polio Epidemic','Spanish Flu','Asian Flu','AIDS pandemic','H1N1 Swine Flu','Ebola Epidemic','Zika Virus epidemic']
print(epidemic_df)

epidemic_df[epidemic_df['jan_sign'] == epidemic_df['FebDec_sign']].year.count()
epidemic_df[['Epidemic/Pandemic', 'year','JanReturn','FebDecReturn']].style.format({'JanReturn': "{:.2%}",'FebDecReturn': "{:.2%}"})

chart_df= epidemic_df[['Epidemic/Pandemic','JanReturn','FebDecReturn']].set_index('Epidemic/Pandemic')
print(chart_df)

fig, ax = plt.subplots(figsize=(25,10))
chart_df.plot.bar(rot=0,ax = ax,fontsize =16)
ax.set_ylabel('Return',fontsize =16)
ax.set_xlabel('Epidemics/Pandemics',fontsize =16)
plt.style.use('seaborn')
ax.set_title("Jan Barometer on Past Epidemic/Pandemic", fontsize =22)

ax.tick_params(axis='both', which='major', labelsize=16)
ax.legend(fontsize=18)
plt.subplots()
plt.show()

print(jan2020)

first = jan2020.Close.iloc[0]
first = 3257.85

last = jan2020.Close.iloc[-1]
last = 3225.52

janrnt = (last-first)/first
print(janrnt)

epidemic_df2 = epidemic_df.append({'year':2020,'Epidemic/Pandemic' : 'COVID-19 pandemic' , 'JanReturn' : janrnt,'FebDecReturn': 0} , ignore_index=True)
epidemic_df2
epidemic_df[['Epidemic/Pandemic', 'year','JanReturn','FebDecReturn']].style.format({'JanReturn': "{:.2%}",'FebDecReturn': "{:.2%}"})

a = epidemic_df2[['Epidemic/Pandemic', 'year','JanReturn','FebDecReturn']].style.format({'JanReturn': "{:.2%}",'FebDecReturn': "{:.2%}"})
print (a)