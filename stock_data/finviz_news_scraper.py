import pandas as pd
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen
from datetime import datetime

# Set up scraper
url = "https://finviz.com/news.ashx"
req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
webpage = urlopen(req).read()
html_content = soup(webpage, "html.parser")

# Function to scrape and process news from Finviz
def scrape_news(html_content, news_index):
    try:
        # Extract news table from HTML content
        news_table = pd.read_html(str(html_content))[news_index]
        # Set column names and drop unnecessary columns
        news_table.columns = ["0", "DateTime", "Headlines"]
        news_table = news_table.drop(columns=['0'])
        news_table = news_table.set_index('DateTime')
        # Set 'Date' as the index column
        return news_table
    except Exception as e:
        # Return error message if scraping fails
        return pd.DataFrame({'Error': [str(e)]})

# Scrape and print general and blog news
print("\nGeneral News:")
print(scrape_news(html_content, 3))

print("\nBlog News:")
print(scrape_news(html_content, 4))