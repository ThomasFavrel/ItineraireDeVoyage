from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
import uvicorn
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import matplotlib.pyplot as plt
# from db_mongo._poi import Poi


api = FastAPI()
templates = Jinja2Templates(directory="templates")  # Chemin vers le répertoire des templates HTML
# Montez le répertoire "static" pour servir des fichiers statiques
api.mount("/static", StaticFiles(directory="static"), name="static")


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
    pois = list(collection.find().limit(10))

    # Fermeture de la connexion à MongoDB
    client.close()

    # Rendu du template HTML avec les données des POI
    return templates.TemplateResponse("poi.html", {"request": request, "pois": pois})

# Route pour tracer les points de latitude et de longitude depuis MongoDB
@api.get("/plot")
async def plot(request: Request):
    
    collection = db["poi"]
    
    # Récupérer les données de latitude et de longitude depuis MongoDB
    poi_data = collection.find({}, {"latitude": 1, "longitude": 1})

    # Extraire les valeurs de latitude et de longitude
    latitude = []
    longitude = []
    for poi in poi_data:
        latitude.append(poi["latitude"])
        longitude.append(poi["longitude"])

    # Passer les données au template HTML pour le rendu
    context = {
        "latitude": latitude,
        "longitude": longitude
    }
    
    print("--------------------> ",request)
    # Rendre le template HTML avec les données
    return templates.TemplateResponse("plot.html", {"request": request, "context": context})
    
# Route pour la page d'accueil
@api.get("/")
async def index(request: Request):
    context = {"background_image": "accueil.jpg"}
    return templates.TemplateResponse("index.html", {"request": request, "context": context})


# Connexion à MongoDB

collection = db['poi']

@api.route("/addpoi", methods=["POST"])
async def add_poi(request: Request):
    form_data = await request.form()
    poi_data = {
        "_id": form_data["_id"],
        "id": form_data["id"],
        "type": form_data["type"],
        "lastUpdate": form_data["lastUpdate"],
        "email": form_data["email"],
        "telephone": form_data["telephone"],
        "typeContact": form_data["typeContact"],
        "homepage": form_data["homepage"],
        "Description": form_data["description"],
        "latitude": form_data["latitude"],
        "longitude": form_data["longitude"],
        "Ville": form_data["Ville"],
        "CodePostale": form_data["CodePostale"],
        "Departement": form_data["Departement"],
        "Region": form_data["Region"],
        "Close": form_data["Close"],
        "Open": form_data["Open"],
        "validFrom": form_data["validFrom"],
        "validThrough": form_data["validThrough"]
    }

    # Insertion du POI dans la collection
    collection.insert_one(poi_data)

    return templates.TemplateResponse("addpoi.html", {"request": request, "success_message": "Le POI a été ajouté avec succès."})

# function for add a new poi
def insert_Poi(poi):
    # Connexion à MongoDB
    client = MongoClient('mongodb://localhost:27017/')

    # Sélection de la base de données et de la collection
    db = client['Poi']
    collection = db['poi']

    # Insertion du POI dans la collection
    collection.insert_one(poi)

    # Fermeture de la connexion à MongoDB
    client.close()

# Route pour ajouter un POI à la base de données
# @api.post("/addpoi")
# def add_poi(poi: _poi.Poi):
#     # Convertir le POI en dictionnaire
#     poi_dict = poi.dict()

#     # Insérer le POI dans MongoDB
#     insert_Poi(poi_dict)

#     return {"message": "POI ajouté avec succès"}