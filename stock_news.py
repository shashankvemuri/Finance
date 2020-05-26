from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import requests
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import os

# Downloading today data from SGX using SGX API
today = datetime.now()
start_date = today-timedelta(1)
start_date = start_date.strftime('%Y%m%d')# Format must be in: '20190808'
end_date = today.strftime('%Y%m%d')
default_folder = './data'

# Start downloading data
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36"}
url = f'https://api.sgx.com/announcements/v1.0/?periodstart={start_date}_160000&periodend={end_date}_155959&pagestart=0&pagesize=20'
res = requests.get(url, headers)

# Store the downloaded data into dataframe (for easier access later)
json_data = res.json()['data']
df = pd.DataFrame(json_data)

# Assuming we are interested in the updates related to "LODHA DEVELOPERS INTERNATIONAL LIMITED"
stock_name = 'LODHA DEVELOPERS INTERNATIONAL LIMITED'

# Filtered out those unwanted company updates information
df = df[df['issuer_name']==stock_name]

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import requests
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import os

def get_pdf(url, folder, filename):
    """
        Downloading the pdf files associated with the specified URL
        and output the downloaded pdf files into specified directory
    """
    based_url = 'https://links.sgx.com'
    pdf_url = based_url+url
    res = requests.get(pdf_url)
    # Create the folder if not exist
    if not os.path.exists(folder):
        os.mkdir(folder)
    # Output pdf file
    with open(os.path.join(folder, filename), 'wb') as f:
        f.write(res.content)
    return

# Get the link to pdf files for each records found
for idx, row in df.iterrows():
    res = requests.get(row['url'])
    soup = BeautifulSoup(res.text)
    # folder = row['issuer_name'].replace(' ', '_')
    # subfolder = row['category_name'].replace(' ', '_')
    try:
        filename = soup.find('a').text
        part_url = soup.find('a')['href']
        get_pdf(part_url, default_folder, filename)
    except:
        # No attached pdf file to be downloaded on specified link
        pass

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import requests
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import os

gauth = GoogleAuth()
# Try to load saved client credentials
gauth.LoadCredentialsFile("mycreds.txt")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile("mycreds.txt")

# Authentication
drive = GoogleDrive(gauth)

# Input destination folder id which you want to upload to.
current_google_folder_id = 'xxxxx' 

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import requests
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import os

def create_folder(drive, folder_name, parent_folder_id):
    """ 
        Create folder on Google Drive
    """
    
    folder_metadata = {
        'title': folder_name,
        # Define the file type as folder
        'mimeType': 'application/vnd.google-apps.folder',
        # ID of the parent folder        
        'parents': [{"kind": "drive#fileLink", "id": parent_folder_id}]
    }

    folder = drive.CreateFile(folder_metadata)
    folder.Upload()

    # Return folder informations
    return folder['id']

def upload_file(drive, folder_id, path_to_file, file_title):
    file = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": folder_id}]})
    file.SetContentFile(path_to_file)
    file['title'] = file_title
    file.Upload()
    

# Get File List
file_list = drive.ListFile(
    {'q': "'{}' in parents and trashed=false".format(current_google_folder_id)}
).GetList()

# Get all title of the file list
if len(file_list) == 0:
    folder_id = create_folder(drive, stock_name, current_google_folder_id)
else:
    # Check if folder already exist
    for index, file in enumerate(file_list):
        if file['title'] == stock_name:
            folder_id = file['id']
            break
        elif index == len(file_list) - 1:
            folder_id = create_folder(drive, stock_name, current_google_folder_id)
        else:
            pass

# Loop through all the files, and upload them one by one to folder 
for f in os.listdir(default_folder):
    upload_file(drive, folder_id, os.path.join(default_folder, f), f)
    
for file in os.listdir(default_folder):
    os.remove(os.path.join(default_folder, file))