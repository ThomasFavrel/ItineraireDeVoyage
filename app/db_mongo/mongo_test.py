import os
import csv
import pandas as pd
from datetime import datetime
from pymongo import MongoClient
from mongoengine import connect
from models import POI

# récupérer les informations d'identification de la base de données à partir des variables d'environnement
mongo_user = "root"
mongo_password = "root"
mongo_host = "localhost"
mongo_port = 27017
mongo_db = "db_mongo"

# Créer une instance du client MongoDB
client = MongoClient(f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_db}")
# Connexion par défaut
connect(db=mongo_db, username=mongo_user, password=mongo_password, host=mongo_host, port=mongo_port)

# csv to df
# Chemin vers le fichier CSV
csv_file = "POI.csv"
df = pd.read_csv(csv_file)

# Fonction pour convertir une date/heure de format CSV en objet datetime
def parse_datetime(datetime_str):
    return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S')

# Lecture du fichier CSV et insertion des données dans la collection POI
with open(csv_file, 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        poi = POI(
            # id=row['@id'],
            type=row['type'],
            lastUpdate=datetime.now,
            email=eval(row['schema:email']),
            telephone=eval(row['schema:telephone']),
            typeContact=eval(row['typeContact']),
            homepage=eval(row['foaf:homepage']),
            Description=row['Description'],
            latitude=float(row['schema:geo.schema:latitude']),
            longitude=float(row['schema:geo.schema:longitude']),
            Ville=row['Ville'],
            CodePostale=row['CodePostale'],
            Departement=row['Departement'],
            Region=row['Region'],
            Close=row['Close'],
            Open=row['Open'],
            validFrom=parse_datetime(row['validFrom']),
            validThrough=parse_datetime(row['validThrough'])
        )
        poi.save()

print('Insertion des données terminée.')

client.close()
