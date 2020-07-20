import pandas as pd
import requests
import datetime
import calendar

pd.set_option('display.max_columns', None)

class dividend_calendar:
    # class attributes
    calendars = []
    url = 'https://api.nasdaq.com/api/calendar/dividends'
    hdrs = {'Accept': 'application/json, text/plain, */*',
             'DNT': "1",
             'Origin': 'https://www.nasdaq.com/',
             'Sec-Fetch-Mode': 'cors',
             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0)'}

    def __init__(self, year, month):
          # instance attributes
          self.year = int(year)
          self.month = int(month)

    def date_str(self, day):
        date_obj = datetime.date(self.year, self.month, day)
        date_str = date_obj.strftime(format='%Y-%m-%d')
        return date_str
    
    def scraper(self, date_str):
        params = {'date': date_str}
        page=requests.get(self.url,headers=self.hdrs,params=params)
        dictionary = page.json()
        return dictionary
    
    def dict_to_df(self, dicti):        
        rows = dicti.get('data').get('calendar').get('rows')
        calendar = pd.DataFrame(rows)
        self.calendars.append(calendar)
        return calendar
    
    def calendar(self, day):
        day = int(day)
        date_str = self.date_str(day)      
        dictionary = self.scraper(date_str)
        self.dict_to_df(dictionary)          
        return dictionary
           
if __name__ == '__main__':
    year = 2020
    month = 8
    
    days_in_month = calendar.monthrange(year, month)[1]
    soon = dividend_calendar(year, month)
    function = lambda days: soon.calendar(days)
    
    iterator = list(range(1, days_in_month+1))
    objects = list(map(function, iterator))
    
    concat_df = pd.concat(soon.calendars)
    drop_df = concat_df.dropna(how='any')
    
    final_df = drop_df.set_index('companyName')
    final_df = final_df.drop(columns=['announcement_Date'])
    final_df.columns = ['ticker', 'dividend_date', 'payment_date', 'record_date', 'dividend_rate', 'annual_rate']
    final_df = final_df.sort_values(['annual_rate', 'dividend_rate'], ascending=[False, False])
    print (final_df.head(5))