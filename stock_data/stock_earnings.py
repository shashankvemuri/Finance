# Import dependencies
import pandas as pd
from datetime import datetime, timedelta
from yahoo_earnings_calendar import YahooEarningsCalendar
import dateutil.parser

# Set pandas options to display all columns
pd.set_option('display.max_columns', None)

# Download earnings for a specific date
report_date = datetime.now().date()
yec = YahooEarningsCalendar()
earnings_df_list = yec.earnings_on(report_date)

# Create a dataframe from earnings_day_list and drop unnecessary columns
earnings_day_df = pd.DataFrame(earnings_df_list)
earnings_day_df = earnings_day_df.drop(columns=['gmtOffsetMilliSeconds', 'quoteType', 'timeZoneShortName'])

# Rename columns and reorder dataframe columns
earnings_day_df.columns = ['Ticker', 'Company Name', 'DateTime', 'Type', 'EPS Estimate', 'EPS Actual', 'EPS Surprise PCT']
earnings_day_df = earnings_day_df[['Ticker', 'Company Name', 'DateTime', 'Type', 'EPS Estimate', 'EPS Actual', 'EPS Surprise PCT']]

# Convert datetime to local timezone and display the dataframe
earnings_day_df['DateTime'] = pd.to_datetime(earnings_day_df['DateTime']).dt.tz_localize(None)
print(earnings_day_df)

# Download earnings for a range of dates
DAYS_AHEAD = 7
start_date = datetime.now().date()
end_date = (datetime.now().date() + timedelta(days=DAYS_AHEAD))

yec = YahooEarningsCalendar()
earnings_range_list = yec.earnings_between(start_date, end_date)

# Create a dataframe from earnings_range_list and drop unnecessary columns
earnings_range_df = pd.DataFrame(earnings_range_list)
earnings_range_df = earnings_range_df.drop(columns=['gmtOffsetMilliSeconds', 'quoteType', 'timeZoneShortName'])

# Rename columns and reorder dataframe columns
earnings_range_df.columns = ['Ticker', 'Company Name', 'DateTime', 'Type', 'EPS Estimate', 'EPS Actual', 'EPS Surprise PCT']
earnings_range_df = earnings_range_df[['Ticker', 'Company Name', 'DateTime', 'Type', 'EPS Estimate', 'EPS Actual', 'EPS Surprise PCT']]

# Convert datetime to local timezone and display the dataframe
earnings_range_df['DateTime'] = pd.to_datetime(earnings_range_df['DateTime']).dt.tz_localize(None)
print(earnings_range_df)

# Download earnings for a specific product within a date range
TICKER = 'TWTR'
DAYS_AHEAD = 180
start_date = datetime.now().date()
end_date = (datetime.now().date() + timedelta(days=DAYS_AHEAD))

yec = YahooEarningsCalendar()
earnings_ticker_list = yec.get_earnings_of(TICKER)

# Create a dataframe from earnings_list and filter by date range
earnings_ticker_df = pd.DataFrame(earnings_ticker_list)
earnings_ticker_df['report_date'] = earnings_ticker_df['startdatetime'].apply(lambda x: dateutil.parser.isoparse(x).date())
earnings_ticker_df = earnings_ticker_df.loc[earnings_ticker_df['report_date'].between(start_date, end_date)].sort_values('report_date')
earnings_ticker_df = earnings_ticker_df.drop(columns=['gmtOffsetMilliSeconds', 'quoteType', 'timeZoneShortName', 'report_date'])

# Rename columns and reorder dataframe columns
earnings_ticker_df.columns = ['Ticker', 'Company Name', 'DateTime', 'Type', 'EPS Estimate', 'EPS Actual', 'EPS Surprise PCT']
earnings_ticker_df = earnings_ticker_df[['Ticker', 'Company Name', 'DateTime', 'Type', 'EPS Estimate', 'EPS Actual', 'EPS Surprise PCT']]
earnings_ticker_df['DateTime'] = pd.to_datetime(earnings_ticker_df['DateTime']).dt.tz_localize(None)
print(earnings_ticker_df)