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