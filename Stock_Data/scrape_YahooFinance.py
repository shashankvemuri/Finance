import urllib.request
from bs4 import BeautifulSoup
import re
from urllib.request import urlopen
from openpyxl.utils.dataframe import dataframe_to_rows
from selenium import webdriver

ticker = 'AMD'

# website page scrape
url = f'https://finance.yahoo.com/quote/{ticker}/key-statistics?p={ticker}'

# adding header
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'}

# Request with headers
req = urllib.request.Request(url, headers=headers)
resp = urllib.request.urlopen(req)
html = resp.read()
soup = BeautifulSoup(html, 'html.parser')
print(soup.title)

soup.find_all('table')

# tagged_values = soup.find_all('td', {'class':'Ta(end) Fw(v)'})
tagged_values = soup.find_all('table')

values = [x.get_text() for x in tagged_values]
for value in values:
    print(value)    
print('\n')

# Define the function to get Price/Book ratio from Yahoo finance
def yahooKeyStats(stock):
    try:
        sourceCode = urlopen('https://finance.yahoo.com/quote/'+ticker+'/key-statistics?p='+ticker).read()
        pbr = re.split('Price/Book',sourceCode.decode())[1]
        pbr = pbr.split('</td>')[1]
        pbr = pbr.split(">")[-1]
        #print ('Price/Book ratio of '+ stock+' is '+pbr)
        print(ticker+pbr)
    except:
        print ('failed in the main loop')

yahooKeyStats(ticker)

# url = urlopen(f'https://finance.yahoo.com/quote/'+ticker+'/key-statistics?p='+ticker).read()
# url = f"https://finance.yahoo.com/quote/{ticker}/key-statistics?p={ticker}"
# bs = webdriver.Chrome('/Users/shashank/Documents/Code/Python/Finance/chromedriver')
# bs.get(url)

# counter1 = bs.find_element_by_xpath('//*[@id="Col1-0-KeyStatistics-Proxy"]/section/div[3]/div[1]/div[2]/div/div[1]/div[1]/table/tbody/tr[1]/td[2]')
# url = f'https://finance.yahoo.com/quote/{ticker}/key-statistics?p={ticker}' 
# html = urlopen(url)
# soup = BeautifulSoup(html, "lxml")

# table = soup.find('table')
# rows = table.find_all('tr')

# def parse_table(table):
#     return [
#         [cell.get_text().strip() for cell in row.find_all(['th', 'td'])]
#            for row in table.find_all('tr')]

# parse_table(table)

# url = f'https://finance.yahoo.com/quote/{ticker}/key-statistics?p={ticker}' 
# html = urlopen(url)
# soup = BeautifulSoup(html, "lxml")
# titles = soup.title

# print(titles.string)
# print(titles.p)

# url = urllib.request.urlopen(f'https://finance.yahoo.com/quote/'+ticker+'/key-statistics?p='+ticker).read() # read all of the page
# soup = BeautifulSoup(url,'lxml')

# all_links=soup.find_all("a")
# for link in all_links:
#     print(link.get("href"))

# all_tables=soup.find_all('table')
# print(all_tables)

# rows = soup.find_all(['th', 'tr'])
# print(rows)
