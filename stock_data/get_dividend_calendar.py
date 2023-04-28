# Import dependencies
import pandas as pd
import requests
import datetime
import calendar

# set pandas option to display all columns
pd.set_option('display.max_columns', None)

class DividendCalendar:
    # class attributes
    calendars = [] # store all calendar DataFrames created
    url = 'https://api.nasdaq.com/api/calendar/dividends'
    hdrs = {
        'Accept': 'text/plain, */*',
        'DNT': "1",
        'Origin': 'https://www.nasdaq.com/',
        'Sec-Fetch-Mode': 'cors',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0)'
    }

    def __init__(self, year, month):
        # instance attributes
        self.year = int(year)
        self.month = int(month)

    def date_str(self, day):
        # return a string representation of the date in the format YYYY-MM-DD
        date_obj = datetime.date(self.year, self.month, day)
        date_str = date_obj.strftime(format='%Y-%m-%d')
        return date_str

    def scraper(self, date_str):
        # send GET request to the dividend calendar API and return a JSON dictionary
        params = {'date': date_str}
        dictionary = requests.get(self.url, headers=self.hdrs, params=params).json()
        return dictionary

    def dict_to_df(self, dicti):
        # convert a JSON dictionary into a pandas DataFrame and append it to calendars list
        rows = dicti.get('data').get('calendar').get('rows')
        calendar = pd.DataFrame(rows)
        self.calendars.append(calendar)
        return calendar

    def calendar(self, day):
        # return a dictionary of dividend calendar data for a specific day
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
        soon = DividendCalendar(year, month)

        # use map to apply the calendar method to each day of the month
        function = lambda days: soon.calendar(days)
        iterator = list(range(1, days_in_month+1))
        objects = list(map(function, iterator))

        # concatenate all DataFrames into a single DataFrame
        concat_df = pd.concat(soon.calendars)
        final_df = concat_df.dropna(how='any')

        # set the index to companyName and then reset it
        final_df = final_df.set_index('companyName')
        final_df = final_df.reset_index()

        # drop the announcement_Date column and rename columns for clarity
        final_df = final_df.drop(columns=['announcement_Date'])
        final_df.columns = [
            'Company Name',
            'Ticker',
            'Dividend Date',
            'Payment Date',
            'Record Date',
            'Dividend Rate',
            'Annual Rate'
        ]

        # sort the DataFrame by Annual Rate and Dividend Date, drop duplicates
        final_df = final_df.sort_values(['Annual Rate', 'Dividend Date'], ascending=[False, False])
        final_df = final_df.drop_duplicates()
        return final_df

    except Exception as e:
        return e

# Example usage
print(get_dividends(2020, 12))