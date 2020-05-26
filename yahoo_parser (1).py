import requests
import csv
from lxml import html
from bs4 import BeautifulSoup as bs
import scipy.io as sio

YAHOO_UPDOWN_URL = 'http://finance.yahoo.com/q/ud?s='

tick = 'ZQK'
page = requests.get(YAHOO_UPDOWN_URL + tick, allow_redirects = False)
soup = bs(page.text, features = 'lxml')
tables = soup.find_all('table')
headers = tables.find(['th'])
#headers = table.find('th',{'class':'yfnc_tablehead1'})
data = tables.find(['td'])
#data = table.findAll('td',{'class':'yfnc_tabledata1'})
it = iter([ d.text.strip() for d in data ]) # create an iterator over the textual data
csvrows = list(zip([tick]*(1+len(data)/5),it,it,it,it,it)) # each call to it returns the next data entry, so this zip will create a 5-tuple array

len(data)

with open('tickers.txt','r') as f:
    lines = f.readlines()

tickers = [l.strip() for l in lines if l.strip() != '']
# tickers


out = open('stocks.csv','a')
csvout = csv.writer(out)

headers = None
for tick in tickers:
    print(tick)
    try:
        page = requests.get(YAHOO_UPDOWN_URL + tick)
    except Exception as inst:
        print(inst)
        continue
    soup = bs(page.text)

    table = soup.find(lambda tag: tag.name=='table' and 
                                  'class' in tag and 
                                  tag['class']=="yfnc_datamodoutline1")
    if table == None:
        print("No data found")
        continue
        
    if headers == None:
        headers = table.findAll('th',{'class':'yfnc_tablehead1'})
        #csvout.writerow([u'Ticker'] + [ h.text for h in headers]) # concat 'Ticker' as the first column
        
    data = table.findAll('td',{'class':'yfnc_tabledata1'})    
    print(len(data))
    
    it = iter([ d.text.strip() for d in data ]) # create an iterator over the textual data
    csvrows = list(zip([tick]*(1+len(data)/5),it,it,it,it,it)) # each call to it returns the next data entry, so this zip will create a 5-tuple array
    print(len(csvrows))
    
    #for row in csvrows:
    #    csvout.writerow(row)
    csvout.writerows(csvrows)

out.flush()
out.close()
# csvout.close()        
# close(out)

with open('stocks.csv','r') as infile:
    csvin = csv.reader(infile)
    data = list(map(tuple,csvin))
    
sio.savemat('stocks.mat',{'data':data},do_compression=True)