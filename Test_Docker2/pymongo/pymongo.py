import pandas as pd
import json
from pprint import pprint
from pymongo import MongoClient

objects_path = '/app/Data/JSON/objects/'
index_path = '/app/Data/JSON/index.json'


# HOST = 'localhost'
# PORT = '27020'
# CLIENT = MongoClient('mongodb')

# POIDB = CLIENT.poi_db

def main(objects_path, index_path):
    with open(index_path) as json_data:
        index = json.load(json_data)

    listOfPathJson = []

    for obj in index:
        listOfPathJson.append(objects_path + obj['file'])

    listOfJson = []

    for json_path in listOfPathJson:
        with open(json_path) as json_data:
            jsonObject = json.load(json_data)
            listOfJson.append(jsonObject)

    client = MongoClient(
    host="127.0.0.1",
    port = 27017
    )

    poi_db = client["poi_db"]
    poi_col = POIDB["poi_col"]
    poi_col.insert_many(listOfJson)

if __name__ == "__main__":
    main()