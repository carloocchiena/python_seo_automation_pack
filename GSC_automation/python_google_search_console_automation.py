# to get the complete Google Api package run  $pip install --upgrade google-api-python-client 

from collections import Counter 
import matplotlib.pyplot as plt 
import pandas as pd
import datetime
import httplib2
from apiclient.discovery import build
from collections import defaultdict
from dateutil import relativedelta
from oauth2client import client
from oauth2client import file
from oauth2client import tools
from stop_words import get_stop_words

'''
global vars
'''
# get today date in str format
date_value = datetime.date.today()
today = date_value.strftime("%d_%b_%Y")

# insert here your branded queries. Null value are not accepted, so use a placeholder if any.
branded_queries = "blank"

# add further words to be excluded here
custom = ["!","'","£","$","%","&","(",")","?","^","*","+","/","-"]  
stop_words = get_stop_words("italian") + get_stop_words ("english") + custom

'''
Connect to the API. You will receive only the websites you own (read: https://support.google.com/webmasters/answer/9008080?hl=en)
'''
site = "https://www.yoursite.com"
    
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
DISCOVERY_URI = ('https://www.googleapis.com/discovery/v1/apis/customsearch/v1/rest')

'''
Connecting using the JSON (stored locally) as a secret key
'''
CLIENT_SECRETS_PATH = r'C:\Your\Path' # path to .json file.

flow = client.flow_from_clientsecrets(CLIENT_SECRETS_PATH, scope=SCOPES, message=tools.message_if_missing(CLIENT_SECRETS_PATH))
 
storage = file.Storage(r'C:\Your\Path')

credentials = storage.get()

http = credentials.authorize(http=httplib2.Http())

webmasters_service = build('webmasters', 'v3', http=http)

'''
Make your API Call. You should see the website you OWN printed on the console.
'''
site_list = webmasters_service.sites().list().execute()
 
verified_sites_urls = [s['siteUrl'] for s in site_list['siteEntry'] 
                      if s['permissionLevel'] != 'siteUnverifiedUser' 
                      and s['siteUrl'][:4] == 'http']
 
print ("Verified Properties:")
for site_url in verified_sites_urls:
    print( site_url)

# set timeframe of reporting
end_date = datetime.date.today()-relativedelta.relativedelta(days=3)
start_date = end_date - relativedelta.relativedelta(months=3)

def execute_request(service, property_uri, request):
    return service.searchanalytics().query(siteUrl=property_uri, body=request).execute()
 
request = {
    'startDate': datetime.datetime.strftime(start_date,"%Y-%m-%d"),
    'endDate': datetime.datetime.strftime(end_date,'%Y-%m-%d'),
    'dimensions': ['page','query'],
    'rowLimit': 5000 # arbitrary row limit for tab viz 
}
 
# (optional)adding a device filter to request
device_category = input('Enter device category: MOBILE, DESKTOP or TABLET (leave it blank for all devices): ').strip()
if device_category:
    request['dimensionFilterGroups'] = [{'filters':[{'dimension':'device','expression':device_category}]}]

# request to SearchConsole API
response = execute_request(webmasters_service, site, request)

# create the dataframe
scDict = defaultdict(list)
 
for row in response['rows']:
    scDict['page'].append(row['keys'][0] or 0)
    scDict['query'].append(row['keys'][1] or 0)
    scDict['clicks'].append(row['clicks'] or 0)
    scDict['ctr'].append(row['ctr'] or 0)
    scDict['impressions'].append(row['impressions'] or 0)
    scDict['position'].append(row['position'] or 0)

df = pd.DataFrame(data = scDict)
 
df['clicks'] = df['clicks'].astype('int')
df['ctr'] = df['ctr']*100
df['impressions'] = df['impressions'].astype('int')
df['position'] = df['position'].round(2)
df.sort_values('clicks',inplace=True,ascending=False)

# use this value if you want to exclude the first n value from the SERP. 
# a reasonable value could be within the first 10 entries.  
SERP_results = 0

df_cannibalized = df[df['position'] > SERP_results] 
df_cannibalized = df_cannibalized[~df_cannibalized['query'].str.contains(branded_queries, regex=True)]  
df_cannibalized = df_cannibalized[df_cannibalized.duplicated(subset=['query'], keep=False)] 
df_cannibalized.set_index(['query'],inplace=True)
df_cannibalized.sort_index(inplace=True)
df_cannibalized.reset_index(inplace=True)

# let's import everything on excel
df.to_excel(f"keywords{today}.xlsx")

print (f"keywords{today}.xlsx saved...")

df_cannibalized.to_excel(f"keywords_cannibalized{today}.xlsx")

print (f"keywords_cannibalized{today}.xlsx saved...")

# creating the dictionary with words frequency
words_split = []

for words in scDict["query"]:
    split = words.split(sep = None)[0]
    if split not in stop_words:
        words_split.append(split)
    
ranked_keywords_list = sorted(Counter(words_split).items(), key = lambda x: x[1], reverse = True)

kw_dict = {}

for couple in ranked_keywords_list[:50]: 
    for item in range(0, len(couple), 2):
        kw_dict[couple[item]] = couple[item+1]
        
df_kw = pd.DataFrame.from_dict(kw_dict, orient = "index", columns=["Frequency"])
df_kw.index.name = "Keywords"

df_kw.to_excel(f"kw_frequency{today}.xlsx")
print (f"kw_frequency{today}.xlsx saved...")

# creating the chart, saving it as a .png
plt.figure(num=1, figsize=(16, 8), dpi=100)
plt.tick_params(axis="x", width = 2)
plt.bar(range(len(kw_dict)), list(kw_dict.values()), align = "center")
plt.xticks(range(len(kw_dict)), list(kw_dict.keys()), rotation = "vertical", )
plt.margins(0.01)
plt.subplots_adjust(bottom = 0.15)
plt.title(s = "First 50 search keywords")
plt.xlabel(s = "kewyords")
plt.ylabel(s = "Frequency")
plt.savefig("chart.png")
print ("chart.png saved...")
plt.show()
