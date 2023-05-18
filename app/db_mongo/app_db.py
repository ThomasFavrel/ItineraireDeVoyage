import csv
from pymongo import MongoClient
import pandas as pd

csv_file = 'POI.csv'
db_name = 'poi_db'
collection_name = 'poi'
client = MongoClient('mongodb://localhost:27017/')
db = client[db_name]
collection = db[collection_name]

# convert csv to df
df = pd.read_csv(csv_file)
data = df.to_dict(orient='records')
collection.insert_many(data)
client.close()
print("Données insérées avec succès dans MongoDB.")