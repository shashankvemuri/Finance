'''
import requests
import json

client_id = r'***REMOVED***'
client_secret = r'***REMOVED***'

auth_data = {
    'grant_type'    : 'client_credentials',
    'client_id'     : client_id,
    'client_secret' : client_secret,
    'scope'         : 'read_content read_financial_data read_product_data read_user_profile'
}

# create session instance
session = requests.Session()

# make a POST to retrieve access_token
auth_request = session.post('https://idfs.gs.com/as/token.oauth2', data = auth_data)
access_token_dict = json.loads(auth_request.text)
access_token = access_token_dict['access_token']

# update session headers
session.headers.update({'Authorization':'Bearer '+ access_token})

# test API connectivity
request_url = 'https://api.marquee.gs.com/v1/users/self'
request = session.get(url=request_url)
print(request.text)
'''
from datetime import date
from gs_quant.data import Dataset
from gs_quant.markets.securities import SecurityMaster, AssetIdentifier 
from gs_quant.session import GsSession

client_id = '***REMOVED***'
client_secret = '***REMOVED***'

scopes = GsSession.Scopes.get_default()
GsSession.use(client_id=client_id, client_secret=client_secret, scopes=scopes)

ds = Dataset('USCANFPP_MINI')
print (ds)

gsids = ds.get_coverage()['gsid'].values.tolist()
df = ds.get_data(date(2012, 7, 2), date(2017, 6, 30), gsid=gsids[0:5])

print (df)

for idx, row in df.iterrows():
    marqueeAssetId = row['assetId']
    asset = SecurityMaster.get_asset(marqueeAssetId, AssetIdentifier.MARQUEE_ID)
    df.loc[df['assetId'] == marqueeAssetId, 'assetName'] = asset.name

print (df)