import pandas as pd  
import requests 
import getpass

# API QUERY
# build your own query here: ["https://ga-dev-tools.appspot.com/query-explorer/"]
# query is secured via a 60 min token (to be refreshed)

api_query = "https://www.googleapis.com/analytics/v3/data/ga?ids=ga%3A181295228&start-date=2020-01-01&end-date=today&metrics=ga%3Ausers%2Cga%3Asessions&dimensions=ga%3Adate"

api_query_uri = getpass.getpass('GA Query')                       # get the query URI for GA connection 
r = requests.get(api_query_uri)                                   # get the http request
data= r.json()                                                    # convert data to a readable JSON file 
df = pd.DataFrame(data['rows'])                                   # create the dataframe 
df = df.rename(columns={0: 'Date', 1: 'Sessions', 2: 'Users'})    # name the table colums 
df['Sessions'] = df['Sessions'].astype(int)                       # convert values to integers for data viz 
df['Users'] = df['Users'].astype(int)                             # convert values to integers for data viz
df['Date'] = pd.to_datetime(df['Date'])                           # set X axis to day value 

chart = df.plot.line(x='Date', y=['Sessions', 'Users'], ylim=[0,None], figsize=[10, 6])
chart.show()

# find max and min values and max day and min day of the dataset
max_sessions = max(df["Sessions"])
min_sessions = min(df["Sessions"])
max_day = df.loc[df["Sessions"] == max_sessions, "Date"] 
min_day = df.loc[df["Sessions"] == min_sessions, "Date"]

# print out the day and the value of the max sessions
max_date = print (max_day), print (max_sessions)

# print out the day and the value of the min sessions
min_date = print (min_day), print (min_sessions)

# print the average sessions and users of the dataset
df.mean()