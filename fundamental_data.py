import pandas as pd 

pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 100)

df = pd.read_csv('fundamental_data.csv')
df.rename(columns={'Unnamed: 0': 'Companies'}, inplace=True)
df = df.set_index('Companies')

#print (df.tail(50))

sort_by_ROI= df.sort_values('P/E', ascending = False)
print(sort_by_ROI)