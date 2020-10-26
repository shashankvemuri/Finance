import pandas as pd
import requests
import datetime
import calendar

pd.set_option('display.max_columns', None)

class dividend_calendar:
    # class attributes
    calendars = []
    url = 'https://api.nasdaq.com/api/calendar/dividends'
    hdrs = {'Accept': 'text/plain, */*',
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
        dictionary=requests.get(self.url,headers=self.hdrs,params=params).json()
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
           
def get_dividends(year, month):
    try:
        year = int(year)
        month = int(month)

        month_name = datetime.date(1900, month, 1).strftime('%B')

        days_in_month = calendar.monthrange(year, month)[1]
        soon = dividend_calendar(year, month)
        function = lambda days: soon.calendar(days)
        
        iterator = list(range(1, days_in_month+1))
        objects = list(map(function, iterator))
        
        concat_df = pd.concat(soon.calendars)
        final_df = concat_df.dropna(how='any')
        
        final_df = final_df.set_index('companyName')
        final_df = final_df.reset_index()
        final_df = final_df.drop(columns = ['announcement_Date'])
        
        final_df.columns = ['Company Name', 'Ticker', 'Dividend Date', 'Payment Date', 'Record Date', 'Dividend Rate', 'Annual Rate']
        final_df = final_df.sort_values(['Annual Rate', 'Dividend Date'], ascending=[False, False])
        final_df = final_df.drop_duplicates()
        
        return final_df
        # return render_template('dividendsOutput.html', year=year, month = month, month_name=month_name, tables=[final_df.to_html(classes='data center table-sortable', index=False)], titles=final_df.columns.values)
    
    except Exception as e:
        return e
        # return render_template('error.html', e = e)

print(get_dividends(2020, 12))