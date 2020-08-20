import pandas as pd 
import glob
import os
import datetime

mylist = []
mylist.append(datetime.date.today())
today = mylist[0]

list_files = (glob.glob("/Users/shashank/Documents/Code/Python/Outputs/S&P500/*.csv"))
list_files = sorted(list_files)
new_data = []

interval = 0
while interval < len(list_files):
    try:
        Data = pd.read_csv(list_files[interval]).tail(10)
        pos_move = []
        neg_move = []
        OBV_Value = 0
        count = 0
        while (count < 10):
            if Data.iloc[count,1] < Data.iloc[count,4]:
                pos_move.append(count)
            elif Data.iloc[count,1] > Data.iloc[count,4]:
                neg_move.append(count)
            count += 1
        count2 = 0
        for i in pos_move:
            OBV_Value = round(OBV_Value + (Data.iloc[i,5]/Data.iloc[i,1]))
        for i in neg_move:
            OBV_Value = round(OBV_Value - (Data.iloc[i,5]/Data.iloc[i,1]))
        Stock_Name = ((os.path.basename(list_files[interval])).split(".csv")[0])
        new_data.append([Stock_Name, OBV_Value])
        interval += 1
        print(Stock_Name)
    except Exception as e:
        print (e)
    
df = pd.DataFrame(new_data, columns = ['Stock', 'OBV_Value'])
df["Stocks_Ranked"] = df["OBV_Value"].rank(ascending = False)
df.sort_values("OBV_Value", inplace = True, ascending = False)
df.to_csv(f"/Users/shashank/Documents/Code/Python/Outputs/OBV/{today}.csv", index = False)