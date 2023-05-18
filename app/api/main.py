from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient

api = FastAPI()
templates = Jinja2Templates(directory="templates")


csv_file = 'POI.csv'
db_name = 'poi_db'
client = MongoClient('mongodb://localhost:27017/')
db = client[db_name]


@api.get("/poi")
def get_poi(request: Request):
    # Connexion à MongoDB
    # client = MongoClient('mongodb://localhost:27017/')

    # Sélection de la base de données et de la collection
    # db = client['poi_db']
    collection = db['poi']

    # Récupération des 20 premiers POI
    pois = list(collection.find().limit(5))

    # Fermeture de la connexion à MongoDB
    client.close()

    # Rendu du template HTML avec les données des POI
    return templates.TemplateResponse("poi.html", {"request": request, "pois": pois})