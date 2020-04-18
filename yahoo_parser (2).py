from bs4 import BeautifulSoup 
import requests 
import csv 
import pandas as pd 

names=[]
prices=[]
changes=[]
percentChanges=[]
marketCaps=[]
totalVolumes=[]
circulatingSupplys=[]
 
for i in range(0,11):
    CryptoCurrenciesUrl = "https://in.finance.yahoo.com/most-active?offset="+str(i)+"&amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;amp;count=100"
    r= requests.get(CryptoCurrenciesUrl)
    data=r.text
    soup=BeautifulSoup(data, features = 'lmxl')
 
for listing in soup.find_all('tr', attrs={'class':'SimpleDataTableRow'}):
   for name in listing.find_all('td', attrs={'aria-label':'Name'}):
      names.append(name.text)
   for price in listing.find_all('td', attrs={'aria-label':'Price (intraday)'}):
      prices.append(price.find('span').text)
   for change in listing.find_all('td', attrs={'aria-label':'Change'}):
      changes.append(change.text)
   for percentChange in listing.find_all('td', attrs={'aria-label':'% change'}):
      percentChanges.append(percentChange.text)
   for marketCap in listing.find_all('td', attrs={'aria-label':'Market cap'}):
      marketCaps.append(marketCap.text)
   for totalVolume in listing.find_all('td', attrs={'aria-label':'Avg vol (3-month)'}):
      totalVolumes.append(totalVolume.text)
   for circulatingSupply in listing.find_all('td', attrs={'aria-label':'Volume'}):
      circulatingSupplys.append(circulatingSupply.text)
 
pd.DataFrame({"Names": names, "Prices": prices, "Change": changes, "% Change": percentChanges, "Market Cap": marketCaps, "Average Volume": totalVolumes,"Volume":circulatingSupplys})
