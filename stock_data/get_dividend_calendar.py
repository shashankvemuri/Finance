import pandas as pd
import requests
import datetime
import calendar

# Set pandas option to display all columns
pd.set_option('display.max_columns', None)

class DividendCalendar:
    def __init__(self, year, month):
        # Initialize with the year and month for the dividend calendar
        self.year = year
        self.month = month
        self.url = 'https://api.nasdaq.com/api/calendar/dividends'
        self.hdrs = {
            'Accept': 'text/plain, */*',
            'DNT': "1",
            'Origin': 'https://www.nasdaq.com/',
            'Sec-Fetch-Mode': 'cors',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0)'
        }
        self.calendars = []  # Store all calendar DataFrames

    def date_str(self, day):
        # Convert a day number into a formatted date string
        return datetime.date(self.year, self.month, day).strftime('%Y-%m-%d')

    def scraper(self, date_str):
        # Scrape dividend data from NASDAQ API for a given date
        response = requests.get(self.url, headers=self.hdrs, params={'date': date_str})
        return response.json()

    def dict_to_df(self, dictionary):
        # Convert the JSON data from the API into a pandas DataFrame
        rows = dictionary.get('data').get('calendar').get('rows', [])
        calendar_df = pd.DataFrame(rows)
        self.calendars.append(calendar_df)
        return calendar_df

    def calendar(self, day):
        # Fetch dividend data for a specific day and convert it to DataFrame
        date_str = self.date_str(day)
        dictionary = self.scraper(date_str)
        return self.dict_to_df(dictionary)

def get_dividends(year, month):
    try:
        # Create an instance of DividendCalendar for the given year and month
        dc = DividendCalendar(year, month)
        days_in_month = calendar.monthrange(year, month)[1]

        # Iterate through each day of the month and scrape dividend data
        for day in range(1, days_in_month + 1):
            dc.calendar(day)

        # Combine all the scraped data into a single DataFrame
        concat_df = pd.concat(dc.calendars).dropna(how='any')
        concat_df = concat_df.set_index('companyName').reset_index()
        concat_df = concat_df.drop(columns=['announcement_Date'])
        concat_df.columns = ['Company Name', 'Ticker', 'Dividend Date', 'Payment Date', 
                             'Record Date', 'Dividend Rate', 'Annual Rate']
        concat_df = concat_df.sort_values(['Annual Rate', 'Dividend Date'], ascending=[False, False])
        concat_df = concat_df.drop_duplicates()
        return concat_df
    except Exception as e:
        return e

# Example usage
print(get_dividends(2020, 12))