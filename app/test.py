import requests
from io import BytesIO
import pandas as pd
import json

requests.get('http://localhost:8000/connect')
requests.get('http://localhost:8000/connectDB/db?database=itinerairedevoyage')
request = requests.get('http://localhost:8000/read?table=poi')


df=pd.read_csv(BytesIO(request.content))

print(type(request.content))
#print(json.loads(request.content))
#print(request.content)

print(type(df))
#print(df)

data = json.loads(request.content)
df = pd.DataFrame(data, columns=["id", "nom", "type", "description", "theme", "lastupdate", "type2", "email", "telephone", "homepage", "latitude", "longitude", "ville", "codePostale", "departement", "region", "close", "open", "validFrom", "validThough"])


print(type(df))
print(df.iloc[34])
#df = pd.json_normalize(data[0]["test"])#"id", "nom", "type", "description", "theme", "lastupdate", "type2", "email", "telephone", "homepage", "latitude", "longitude", "ville", "codePostale", "departement", "region", "close", "open", "validFrom", "validThough"])
#print(df)
"""
from urllib.request import urlopen
import json

urlopen('http://localhost:8000/connect')
urlopen('http://localhost:8000/connectDB/db?database=itinerairedevoyage')
html = urlopen('http://localhost:8000/read?table=poi').read()

print(type(json.load(html)))
#print(json.load(html))
print(type(html))
print(html)

import urllib.request
request = urllib.request.Request('http://localhost:8000/read?table=poi')
response = urllib.request.urlopen(request)
print(type(response.read().decode('utf-8')))"""