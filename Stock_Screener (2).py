import urllib.request
import urllib.parse
import json
import pandas as pd
import re
import os
import sys
import smtplib
import email
import email.mime
import email.mime.text
import email.mime.multipart
import time
import configparser


class StockScreener(object):
    """
    StockScreener class
    What it does:
        - Sends a request to Google Stock Screener API based on certain screening criteria and exchanges (see below),
        - Saves the JSON response locally, converts the relevant information into a CSV file
        - Sends this information in a nicely formatted table to a specified e-mail address.
    Limitations:
        This implementation supports a maximum of 8 screening criterias for stock.
        The Google stock screener supports a maximum of 12 but - hey - I think 8 criterias is more than enough!
        If you intend to implement less than 8 criteria, please leave empty the unutilised ones (e.g. CRITERIA6 = "")
    Available Screening Criterias (use in the config.ini file, without quotes):
        > Criteria Category:
            "criteria_name"
        > Popular Criteria:
            "forward_pe_1year", "change_today_percent", "price_to_book",
            "price_to_sales_trailing_12months",
        > Price Criteria:
            "last_price", "earnings_per_share", "high_52week", "low_52week",
            "price_change_52week", "average_50day_price", "average_150day_price",
            "average_200day_price", "price_change_26week" "price_change_13week"
        > Valuation Criteria:
            "market_cap", "pe_ratio", "forward_pe_1year"
        > Dividend Criteria:
            "dividend_recent_quarter", "dividend_next_quarter", "dividend_per_share"
            "dividend_next_year", "dividend_per_share_trailing_12months",
            "dividend_yield", "dividend_recent_year"
        > Financial Ratios Criteria:
            "book_value_per_share_year", "cash_per_share_year", "current_assets_to_liabilities_ratio_year",
            "longterm_debt_to_assets_year", "longterm_debt_to_assets_quarter",
            "total_debt_to_assets_year", "total_debt_to_assets_quarter",
            "longterm_debt_to_equity_year", "longterm_debt_to_equity_quarter",
            "total_debt_to_equity_year", "total_debt_to_equity_quarter"
        > Operating Metrics Criteria:
            "interest_coverage_year", "return_on_investment_trailing_12months",
            "return_on_investment_5years", "return_on_investment_year",
            "return_on_assets_year", "return_on_assets_5years", "return_on_assets_trailing_12months",
            "return_on_equity_year", "return_on_equity_5years", "return_on_equity_trailing_12months"
        > Stock Metrics Criteria:
            "beta", "shares_floating", "percent_institutional_held",
            "volume", "average_volume"
        > Margins Criteria:
            "gross_margin_trailing_12months", "ebitd_margin_trailing_12months",
            "operating_margin_trailing_12months", "net_profit_margin_percent_trailing_12months"
        > Growth Criteria:
            "net_income_growth_rate_5years", "revenue_growth_rate_5years",
            "revenue_growth_rate_10years", "eps_growth_rate_5years", "eps_growth_rate_10years"
    Available Stock Exchanges:
        Stock Exchange Name |--| Stock Exchange Code(s) |--| Currencies:
        1) US Markets |--| OTCMKTS,OTCBB,NYSEMKT,NYSEARCA,NYSE,NASDAQ |--|
        2) London Stock Exchange |--| LON |--| GBP,GBX
        3) Italian Stock Exchange |--| BIT |--|
        4) Canadian Markets |--| TSE,CVE,CNX |--|
        5) Swiss Markets |--| VTX,SWX |--|
        6) Danish Stock Exchange |--| CPH |--| DKK
        7) German Stock Exchanges |--| ETR,FRA |--| EUR,USD
        8) Spanish Stock Exchange |--| BME |--| EUR
        9) Tokyo Stock Exchange |--| TYP |--| JPY
        10) Warsaw Stock Exchange |--| WSE |--| PLN
        11) Stockholm Stock Exchange |--| STO |--| NOK, SEK
        12) Johannesburg Stock Exchange |--| JSE |--| ZAR, ZAK
        13) Singapore Stock Exchange |--| SGX |--|
        14) Moscow Stock Exchange |--| MCX |--| RUB
        15) Amsterdam Stock Exchange |--| AMS |--|
        16) Korean Stock Exchanges |--| KOSDAQ, KRX |--| KRW
        17) Bruxelles Stock Exchange |--| EBR |--|
        18) Euronext Paris Stock Exchange |--| EPA |--|
        19) Australian Stock Exchange |--| ASX |--| AUD
        20) Chinese Stock Exchanges |--| SHE, SHA |--|
        21) Hong Kong Stock Exchanges |--| HKG |--|
        22) Tel Aviv Stock Exchange |--| TLV |--| ILS, ILA
        23) Indian Stock Exchanges |--| NSE, BOM |--| INR
        24) Turkish Stock Exchange |--| IST |--| TRY
        25) Taiwan Stock Exchange |--| TPE |--| TWD
        26) Lithuanian Stock Exchange |--| VSE |--| EUR
        27) Buenos Aires Stock Exchange |--| BCBA |--| ARS
        28) Vienna Stock Exchange |--| VIE |--| EUR
        29) Brazilian Stock Echange |--| BVMF |--| BRL
        30) Estonia Stock Exchange |--| TAL |--| EUR
        31) Finnish Stock Exchange |--| HEL |--| EUR
        32) Iceland Stock Exchange |--| ICE |--|
        33) Latvian Stock Exchange |--| RSE |--|
        34) New Zealand Stock Exchange |--| NZE |--| NZD
        35) Lisbon Stock Exchange |--| ELI |--| EUR
        36) Riyad Stock Exchange |--| TADAWUL |--| SAR
        37) Thai Stock Exchange |--| BKK |--| THB
    Available Sectors:
        **** TODO *****
    """

    COMPANY_NAME = "AAPL"

    CRITERIA1 = "market_cap" # placeholder
    CRITERIA2 = "pe_ratio" # placeholder
    CRITERIA3 = "return_on_investment_trailing_12months" # placeholder
    CRITERIA4 = "beta" # placeholder
    CRITERIA5 = "last_price" # placeholder
    CRITERIA6 = "" # placeholder
    CRITERIA7 = "" # placeholder
    CRITERIA8 = "" # placeholder

    EXCHANGE_STRING = "NYSE"
    CURRENCY_STRING = "USD"
    SECTOR_STRING = "sector"

    CRITERIA1_MIN = 1000000000 # placeholder
    CRITERIA1_MAX = 5000000000000 # placeholder

    CRITERIA2_MIN = 10 # placeholder
    CRITERIA2_MAX = 30 # placeholder

    CRITERIA3_MIN = 5 # placeholder
    CRITERIA3_MAX = 300 # placeholder

    CRITERIA4_MIN = -2 # placeholder
    CRITERIA4_MAX = 3 # placeholder

    CRITERIA5_MIN = 2 # placeholder
    CRITERIA5_MAX = 1000 # placeholder

    CRITERIA6_MIN = 0 # placeholder
    CRITERIA6_MAX = 0 # placeholder

    CRITERIA7_MIN = 0 # placeholder
    CRITERIA7_MAX = 0 # placeholder

    CRITERIA8_MIN = 0 # placeholder
    CRITERIA8_MAX = 0 # placeholder

    def __init__(self, exchanges, currency='', sector=''):
        """
        Class initialiser
        :param exchanges: the selected exchange(s)
        :param currency: the selected currency(ies)
        :param sector: the selected sector
        """
        self.urlBeginning = 'https://finance.google.com/finance?output=json&start=0&num=3000&noIL=1&q='
        self.exchanges = exchanges
        self.currency = currency
        self.sector = sector
        self.urlClosing = '&restype=company&ei=gNeJWeBdj-SwAYyinoAO'

    def createexchanges(self):
        """
        Creates the String with the list of exchanges to be injected in the request
        :return: exchangeString
        """
        exchangeString = ""
        if type(self.exchanges) is not list:
            raise Exception("Exchanges need to be structured as a list")
        if len(self.exchanges) == 1:
            exchangeString += '(' + str(self.EXCHANGE_STRING) + ' == "' + self.exchanges[0] + '")'
        elif len(self.exchanges) > 1:
            exchangeString += '('
            for exchange in self.exchanges[:-1]:
                exchangeString += '(' + str(self.EXCHANGE_STRING) + ' == "' + exchange + '")'
                exchangeString += ' | '
            exchangeString += '(' + str(self.EXCHANGE_STRING) + ' == "' + self.exchanges[-1] + '")'
            exchangeString += ')'
        return exchangeString

    def formMidUrl(self):
        """
        Forms the middle part of the URL
        :return: midUrlString
        """
        midUrlString = ''
        midUrlString += '['

        if len(self.sector) > 0:
            midUrlString += str(self.SECTOR_STRING) + ' == "' + str(self.sector) + '" & '

        if len(self.currency) > 0:
            midUrlString += str(self.CURRENCY_STRING) + ' == "' + str(self.currency) + '" & '

        midUrlString += str(self.createexchanges())

        if len(self.CRITERIA1) > 0:
            midUrlString += ' & (' + str(self.CRITERIA1) + ' >= ' + str(self.CRITERIA1_MIN) + ') & (' + str(self.CRITERIA1) + ' <= ' + str(self.CRITERIA1_MAX) + ')'

        if len(self.CRITERIA2) > 0:
            midUrlString += ' & (' + str(self.CRITERIA2) + ' >= ' + str(self.CRITERIA2_MIN) + ') & (' + str(self.CRITERIA2) + ' <= ' + str(self.CRITERIA2_MAX) + ')'

        if len(self.CRITERIA3) > 0:
            midUrlString += ' & (' + str(self.CRITERIA3) + ' >= ' + str(self.CRITERIA3_MIN) + ') & (' + str(self.CRITERIA3) + ' <= ' + str(self.CRITERIA3_MAX) + ')'

        if len(self.CRITERIA4) > 0:
            midUrlString += ' & (' + str(self.CRITERIA4) + ' >= ' + str(self.CRITERIA4_MIN) + ') & (' + str(self.CRITERIA4) + ' <= ' + str(self.CRITERIA4_MAX) + ')'

        if len(self.CRITERIA5) > 0:
            midUrlString += ' & (' + str(self.CRITERIA5) + ' >= ' + str(self.CRITERIA5_MIN) + ') & (' + str(self.CRITERIA5) + ' <= ' + str(self.CRITERIA5_MAX) + ')'

        if len(self.CRITERIA6) > 0:
            midUrlString += ' & (' + str(self.CRITERIA6) + ' >= ' + str(self.CRITERIA6_MIN) + ') & (' + str(self.CRITERIA6) + ' <= ' + str(self.CRITERIA6_MAX) + ')'

        if len(self.CRITERIA7) > 0:
            midUrlString += ' & (' + str(self.CRITERIA7) + ' >= ' + str(self.CRITERIA7_MIN) + ') & (' + str(self.CRITERIA7) + ' <= ' + str(self.CRITERIA7_MAX) + ')'

        if len(self.CRITERIA8) > 0:
            midUrlString += ' & (' + str(self.CRITERIA8) + ' >= ' + str(self.CRITERIA8_MIN) + ') & (' + str(self.CRITERIA8) + ' <= ' + str(self.CRITERIA8_MAX) + ')'

        midUrlString += ']'
        print('Your Screen Query: ' + midUrlString)

        return midUrlString

    def formFullURL(self):
        """
        Composes the full URL
        :return: fullURL
        """
        return self.urlBeginning + urllib.parse.quote(self.formMidUrl()) + self.urlClosing

    def getdataintoJSON(self, fullUrl, fileName):
        """
        Gets the data in a local JSON file
        :param fullUrl: The full URL request to the Google StockScreener service
        :param fileName: The JSON file name that will be saved locally
        :return: None
        """
        with urllib.request.urlopen(fullUrl) as url:
            decoded_json = url.read().decode()
            updated_json = re.sub(r"\\", '', decoded_json)
            data = json.loads(updated_json)
            with open(fileName, 'w') as outfile:
                json.dump(data, outfile)

    def structureDataAsCSV(self, JSONfile, CSVfile):
        """
        Structure the data in a CSV format, and saves to a CSV file
        :param JSONfile: The JSON file that was saved locally and that contains the response from the server
        :param CSVfile: The CSV file name to be saved locally
        :return: None
        """
        with open(JSONfile) as inputfile:
            data = json.load(inputfile)

        resultString = ""
        resultString += str(self.COMPANY_NAME) + ', ' + str(self.EXCHANGE_STRING)

        if len(self.CRITERIA1) > 0:
            resultString += ', ' + str(self.CRITERIA1)

        if len(self.CRITERIA2) > 0:
            resultString += ', ' + str(self.CRITERIA2)

        if len(self.CRITERIA3) > 0:
            resultString += ', ' + str(self.CRITERIA3)

        if len(self.CRITERIA4) > 0:
            resultString += ', ' + str(self.CRITERIA4)

        if len(self.CRITERIA5) > 0:
            resultString += ', ' + str(self.CRITERIA5)

        if len(self.CRITERIA6) > 0:
            resultString += ', ' + str(self.CRITERIA6)

        if len(self.CRITERIA7) > 0:
            resultString += ', ' + str(self.CRITERIA7)

        if len(self.CRITERIA8) > 0:
            resultString += ', ' + str(self.CRITERIA8)

        resultString += "\n"

        for item in data['searchresults']:
            resultString += item['title'].replace(",", "") + ", " + item['exchange'] + ", "
            for indicator in item['columns']:
                resultString += indicator['value'] + ", "
            resultString = resultString[:-2]
            resultString += "\n"

        with open(CSVfile, 'w') as outputfile:
            outputfile.write(resultString)

    def loaddataintoPandasarray(self, CSVfilename):
        """
        Loads the CSV data in a pandas DataFrame
        :param CSVfilename: The CSV file name that was saved locally and contains the data in CSV format
        :return: dataframe: The Pandas dataframe containing a stock screen output
        """
        dataframe = pd.read_csv(CSVfilename, index_col=False, header=0)
        return dataframe

    def sendStockScreenerViaEmail(self, data, email_address_recipient, email_address_username, pwd, server_name, port):
        """
        Note: sends an HTML-formatted email by default... would be good to have a recipient address
        that can accept HTML-formatted emails
        :param data: The data to be sent (should be in the form of a pandas dataframe)
        :param email_address_recipient: The recipient of the email
        :param email_address_username: The sender of the email, usually the username to access the mail server
        :param pwd: The password of the email sender
        :param server_name: The email server to connect to
        :param port: The port that where the email server accepts connections
        :return:
        """
        # You must configure these smpt-server settings before using this script
        use_tsl = True  # For Gmail use True
        smpt_server_requires_authentication = True  # For Gmail use True
        smtp_username = 'johnbroe23@gmail.com'  # This is the smtp server username and also the sender name of the email.
        smtp_password = 'fantasyforlife3'
        smtp_server_name = 'smtp.gmail.com'  # For Gmail use smtp.gmail.com
        smtp_server_port = 587  # For Gmail use 587
        adesso = time.strftime("%c")  # what time is it now?

        # Example email message contents
        message_recipient = 'shashankv323@gmail.com'
        message_title = 'Google StockScreener - ' + adesso
        message_text_list = data.to_html(justify='left')
        message_attachment_path = ''  # Set this to the full path of the file you want to attach to the mail or to '' if you do not want to attach anything.

        # Compile the start of the email message.
        email_message_content = email.mime.multipart.MIMEMultipart('alternative')
        email_message_content['From'] = smtp_username
        email_message_content['To'] = message_recipient
        email_message_content['Subject'] = message_title

        # Append the user given lines of text to the email message.
        email_message_content.attach(email.mime.text.MIMEText(message_text_list.encode('utf-8'), _charset='utf-8', _subtype='html'))

        # Read attachment file, encode it and append it to the email message.
        if message_attachment_path != '':  # If no attachment path is defined, do nothing.
            email_attachment_content = email.mime.base.MIMEBase('application', 'octet-stream')
            email_attachment_content.set_payload(open(message_attachment_path, 'rb').read())
            email.encoders.encode_base64(email_attachment_content)
            email_attachment_content.add_header('Content-Disposition',
                                                'attachment; filename="%s"' % os.path.basename(message_attachment_path))
            email_message_content.attach(email_attachment_content)

        # Email message is ready, before sending it, it must be compiled  into a long string of characters.
        email_message_content_string = email_message_content.as_string()

        # Start communication with the smtp-server.
        try:
            mailServer = smtplib.SMTP(smtp_server_name, smtp_server_port, 'localhost',
                                      15)  # Timeout is set to 15 seconds.
            mailServer.ehlo()

            # Check if message size is below the max limit the smpt server announced.
            message_size_is_within_limits = True  # Set the default that is used if smtp-server does not annouce max message size.
            if 'size' in mailServer.esmtp_features:
                server_max_message_size = int(
                    mailServer.esmtp_features['size'])  # Get smtp server announced max message size
                message_size = len(email_message_content_string)  # Get our message size
                if message_size > server_max_message_size:  # Message is too large for the smtp server to accept, abort sending.
                    message_size_is_within_limits = False
                    print('Message_size (', str(message_size), ') is larger than the max supported size (',
                          str(server_max_message_size), ') of server:', smtp_server_name, 'Sending aborted.')
                    sys.exit(1)
            if message_size_is_within_limits == True:
                # Uncomment the following line if you want to see printed out the final message that is sent to the smtp server
                # print('email_message_content_string =', email_message_content_string)
                if use_tsl == True:
                    mailServer.starttls()
                    mailServer.ehlo()  # After starting tls, ehlo must be done again.
                if smpt_server_requires_authentication == True:
                    mailServer.login(smtp_username, smtp_password)
                mailServer.sendmail(smtp_username, message_recipient, email_message_content_string)
            mailServer.close()
            print("Email sent!")

        except smtplib.socket.timeout as reason_for_error:
            print('Error, Timeout error:', reason_for_error)
            sys.exit(1)
        except smtplib.socket.error as reason_for_error:
            print('Error, Socket error:', reason_for_error)
            sys.exit(1)
        except smtplib.SMTPRecipientsRefused as reason_for_error:
            print('Error, All recipients were refused:', reason_for_error)
            sys.exit(1)
        except smtplib.SMTPHeloError as reason_for_error:
            print('Error, The server didn’t reply properly to the HELO greeting:', reason_for_error)
            sys.exit(1)
        except smtplib.SMTPSenderRefused as reason_for_error:
            print('Error, The server didn’t accept the sender address:', reason_for_error)
            sys.exit(1)
        except smtplib.SMTPDataError as reason_for_error:
            print(
                'Error, The server replied with an unexpected error code or The SMTP server refused to accept the message data:',
                reason_for_error)
            sys.exit(1)
        except smtplib.SMTPException as reason_for_error:
            print(
                'Error, The server does not support the STARTTLS extension or No suitable authentication method was found:',
                reason_for_error)
            sys.exit(1)
        except smtplib.SMTPAuthenticationError as reason_for_error:
            print('Error, The server didn’t accept the username/password combination:', reason_for_error)
            sys.exit(1)
        except smtplib.SMTPConnectError as reason_for_error:
            print('Error, Error occurred during establishment of a connection with the server:', reason_for_error)
            sys.exit(1)
        except RuntimeError as reason_for_error:
            print('Error, SSL/TLS support is not available to your Python interpreter:', reason_for_error)
            sys.exit(1)


if __name__ == '__main__':

    # Set absolute path
    screener_bot_path = os.path.dirname(os.path.abspath('/Users/shashank/Downloads/'))

    # Config File Name (see template in config_sample.ini)
    configFileName = 'config.ini'
    config = configparser.ConfigParser()
    config.read(os.path.join(screener_bot_path, configFileName))

    #Screener Data
    exchanges_config = config['screener_data']['exchanges'].replace(" ","").split(',')
    exchanges = [exchange.upper() for exchange in exchanges_config]
    currency = config['screener_data']['currency'].upper()
    fileName = os.path.join(screener_bot_path, config['screener_data']['screener.json'])
    csvfile = os.path.join(screener_bot_path, config['screener_data']['screener.csv'])
    sector = config['screener_data']['sector'].upper()

    #Email Data
    recipient = config['email_data']['recipient']
    sender = config['email_data']['sender']
    pwd_sender = config['email_data']['pwd_sender']
    server_name = config['email_data']['server_name']
    server_port = config['email_data']['server_port']

    #Main method
    stockScreener = StockScreener(exchanges, currency, sector) # class begins

    # Criteria Setting
    stockScreener.CRITERIA1 = config['screening_criteria']['CRITERIA1'].lower()
    stockScreener.CRITERIA2 = config['screening_criteria']['CRITERIA2'].lower()
    stockScreener.CRITERIA3 = config['screening_criteria']['CRITERIA3'].lower()
    stockScreener.CRITERIA4 = config['screening_criteria']['CRITERIA4'].lower()
    stockScreener.CRITERIA5 = config['screening_criteria']['CRITERIA5'].lower()
    stockScreener.CRITERIA6 = config['screening_criteria']['CRITERIA6'].lower()
    stockScreener.CRITERIA7 = config['screening_criteria']['CRITERIA7'].lower()
    stockScreener.CRITERIA8 = config['screening_criteria']['CRITERIA8'].lower()

    stockScreener.CRITERIA1_MIN = float(config['screening_criteria']['CRITERIA1_MIN']) if len(config['screening_criteria']['CRITERIA1_MIN']) > 0 else 0
    stockScreener.CRITERIA1_MAX = float(config['screening_criteria']['CRITERIA1_MAX']) if len(config['screening_criteria']['CRITERIA1_MAX']) > 0 else 0

    stockScreener.CRITERIA2_MIN = float(config['screening_criteria']['CRITERIA2_MIN']) if len(config['screening_criteria']['CRITERIA2_MIN']) > 0 else 0
    stockScreener.CRITERIA2_MAX = float(config['screening_criteria']['CRITERIA2_MAX']) if len(config['screening_criteria']['CRITERIA2_MAX']) > 0 else 0

    stockScreener.CRITERIA3_MIN = float(config['screening_criteria']['CRITERIA3_MIN']) if len(config['screening_criteria']['CRITERIA3_MIN']) > 0 else 0
    stockScreener.CRITERIA3_MAX = float(config['screening_criteria']['CRITERIA3_MAX']) if len(config['screening_criteria']['CRITERIA3_MAX']) > 0 else 0

    stockScreener.CRITERIA4_MIN = float(config['screening_criteria']['CRITERIA4_MIN']) if len(config['screening_criteria']['CRITERIA4_MIN']) > 0 else 0
    stockScreener.CRITERIA4_MAX = float(config['screening_criteria']['CRITERIA4_MAX']) if len(config['screening_criteria']['CRITERIA4_MAX']) > 0 else 0

    stockScreener.CRITERIA5_MIN = float(config['screening_criteria']['CRITERIA5_MIN']) if len(config['screening_criteria']['CRITERIA5_MIN']) > 0 else 0
    stockScreener.CRITERIA5_MAX = float(config['screening_criteria']['CRITERIA5_MAX']) if len(config['screening_criteria']['CRITERIA5_MAX']) > 0 else 0

    stockScreener.CRITERIA6_MIN = float(config['screening_criteria']['CRITERIA6_MIN']) if len(config['screening_criteria']['CRITERIA6_MIN']) > 0 else 0
    stockScreener.CRITERIA6_MAX = float(config['screening_criteria']['CRITERIA6_MAX']) if len(config['screening_criteria']['CRITERIA6_MAX']) > 0 else 0

    stockScreener.CRITERIA7_MIN = float(config['screening_criteria']['CRITERIA7_MIN']) if len(config['screening_criteria']['CRITERIA7_MIN']) > 0 else 0
    stockScreener.CRITERIA7_MAX = float(config['screening_criteria']['CRITERIA7_MAX']) if len(config['screening_criteria']['CRITERIA7_MAX']) > 0 else 0

    stockScreener.CRITERIA8_MIN = float(config['screening_criteria']['CRITERIA8_MIN']) if len(config['screening_criteria']['CRITERIA8_MIN']) > 0 else 0
    stockScreener.CRITERIA8_MAX = float(config['screening_criteria']['CRITERIA8_MAX']) if len(config['screening_criteria']['CRITERIA8_MAX']) > 0 else 0

    # Main method starts
    stockScreenerUrl = stockScreener.formFullURL() # forms full url
    stockScreener.getdataintoJSON(stockScreenerUrl, fileName) # get data into JSON
    stockScreener.structureDataAsCSV(fileName, csvfile) # load from JSON to CSV
    df = stockScreener.loaddataintoPandasarray(csvfile) # Load into pandas array
    print(df)

    # Set send to True if you want to use email module and send
    send = config['email_data']['send_email'].lower()

    if send == "true":
        print("\nSending....")
        stockScreener.sendStockScreenerViaEmail(df,
                                                recipient, sender, pwd_sender,
                                                server_name, server_port) # send via email
    else:
        print("\nClosing module without sending....")
        