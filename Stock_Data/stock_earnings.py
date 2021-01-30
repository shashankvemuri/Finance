import pandas as pd
from datetime import datetime
from datetime import timedelta
from yahoo_earnings_calendar import YahooEarningsCalendar
import dateutil.parser

pd.set_option('display.max_columns', None)

# Downloading the earnings for a specific date
report_date = datetime.now().date()
yec = YahooEarningsCalendar()
earnings_list = yec.earnings_on(report_date)

earnings_df = pd.DataFrame(earnings_list)
earnings_df = earnings_df.drop(columns = ['gmtOffsetMilliSeconds', 'quoteType', 'timeZoneShortName'])
earnings_df.columns = ['Ticker', 'Company Name', 'DateTime', 'Type', 'EPS Estimate', 'EPS Actual', 'EPS Surprise PCT']
earnings_df = earnings_df[['Ticker', 'Company Name', 'DateTime', 'Type', 'EPS Estimate', 'EPS Actual', 'EPS Surprise PCT']]
earnings_df['DateTime'] = pd.to_datetime(earnings_df['DateTime']).dt.tz_localize(None)
print(earnings_df)

# Downloading the earnings for a range of dates
DAYS_AHEAD = 7
start_date = datetime.now().date()
end_date = (datetime.now().date() + timedelta(days=DAYS_AHEAD))

yec = YahooEarningsCalendar()
earnings_list = yec.earnings_between(start_date, end_date)

earnings_df = pd.DataFrame(earnings_list)
earnings_df = earnings_df.drop(columns = ['gmtOffsetMilliSeconds', 'quoteType', 'timeZoneShortName'])
earnings_df.columns = ['Ticker', 'Company Name', 'DateTime', 'Type', 'EPS Estimate', 'EPS Actual', 'EPS Surprise PCT']
earnings_df = earnings_df[['Ticker', 'Company Name', 'DateTime', 'Type', 'EPS Estimate', 'EPS Actual', 'EPS Surprise PCT']]
earnings_df['DateTime'] = pd.to_datetime(earnings_df['DateTime']).dt.tz_localize(None)
print(earnings_df)

# Downloading the earnings for a specific product
TICKER = 'TWTR'
DAYS_AHEAD = 180
start_date = datetime.now().date()
end_date = (datetime.now().date() + timedelta(days=DAYS_AHEAD))

yec = YahooEarningsCalendar()
earnings_list = yec.get_earnings_of(TICKER)
earnings_df = pd.DataFrame(earnings_list)

earnings_df['report_date'] = earnings_df['startdatetime'].apply(lambda x: dateutil.parser.isoparse(x).date())
earnings_df = earnings_df.loc[earnings_df['report_date'].between(start_date, end_date)] \
                          .sort_values('report_date')
earnings_df = earnings_df.drop(columns = ['gmtOffsetMilliSeconds', 'quoteType', 'timeZoneShortName', 'report_date'])
earnings_df.columns = ['Ticker', 'Company Name', 'DateTime', 'Type', 'EPS Estimate', 'EPS Actual', 'EPS Surprise PCT']
earnings_df = earnings_df[['Ticker', 'Company Name', 'DateTime', 'Type', 'EPS Estimate', 'EPS Actual', 'EPS Surprise PCT']]
earnings_df['DateTime'] = pd.to_datetime(earnings_df['DateTime']).dt.tz_localize(None)
print(earnings_df)