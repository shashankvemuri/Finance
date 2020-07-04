from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import requests

ticker = 'AAPL'
url = f'https://finance.yahoo.com/quote/{ticker}/key-statistics?p={ticker}' 
html = urlopen(url)
soup = BeautifulSoup(html, "lxml")


all_tables=soup.find_all('table')
print(all_tables)

tables = soup.find('table', {'class': "table-qsp-stats Mt(10px)"})


for table in all_tables:
    print ("###############")
    print (table.text[::])

res = requests.get(f'https://finance.yahoo.com/quote/{ticker}/key-statistics?p={ticker}')
soup = BeautifulSoup(res.content,'lxml')
table = soup.find_all('table')[0]
df = pd.read_html(str(table))[0]
print(df)

res = requests.get(f'https://finance.yahoo.com/quote/{ticker}/key-statistics?p={ticker}')
soup = BeautifulSoup(res.content,'lxml')
table_body=soup.find('table')
rows = table_body.find_all('tr')
for row in rows:
    cols=row.find_all('td')
    cols=[x.text.strip() for x in cols]
    print(cols)

print(soup.prettify())

list(soup.children)

tables = pd.read_html(f"https://finance.yahoo.com/quote/{ticker}/key-statistics?p={ticker}")
print(tables[0:])

tables = pd.read_html(f"https://finance.yahoo.com/quote/{ticker}/key-statistics?p={ticker}", header=0)
print(tables[0:])

def parse_table(table):
    """ Get data from table """
    return [
        [cell.get_text().strip() for cell in row.find_all(['th', 'td'])]
           for row in table.find_all('tr')]

parse_table(table)