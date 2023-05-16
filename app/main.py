from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
    

# from db.models import MongoDB, POI

# # Connexion à la base de données
# mongo = MongoDB("db_mongo", 27017, "db_mongo")

# # Ajout d'un point d'intérêt
# new_poi = POI("1", "restaurant", "2022-05-09", ["contact@restaurant.com"], ["0123456789"], ["phone"], "http://www.restaurant.com", "Description du restaurant", "48.8534", "2.3488", "Paris", "75001", "Île-de-France", "Île-de-France", "22:00:00", "12:00:00", "2022-05-01", "2022-05-31")
# mongo.add_poi(new_poi)

# # Affichage de tous les points d'intérêt dans la collection MongoDB
# for poi in mongo.poi_collection.find():
#     print(poi)
