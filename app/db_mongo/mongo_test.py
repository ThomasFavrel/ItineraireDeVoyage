import pandas as pd

# create MongoDB instance
mongo = MongoDB("localhost", 27017, "db_mongo")

# read POI data from CSV file
poi_data = pd.read_csv("poi_data.csv")

# iterate over rows in the CSV file and create POI instances
for index, row in poi_data.iterrows():
    poi = POI(row['id'], row['type'], row['last_update'], row['emails'], row['telephones'], row['contact_types'], row['homepage'], row['description'], row['latitude'], row['longitude'], row['city'], row['postal_code'], row['department'], row['region'], row['close'], row['open'], row['valid_from'], row['valid_through'])
    
    # add POI instance to MongoDB
    mongo.add_poi(poi)
