from pymongo import MongoClient

class Poi:
    def __init__(self, data):
        self._id = data['_id']
        self.id = data['id']
        self.type = data['type']
        self.lastUpdate = data['lastUpdate']
        self.email = data['email']
        self.telephone = data['telephone']
        self.typeContact = data['typeContact']
        self.homepage = data['homepage']
        self.Description = data['Description']
        self.latitude = data['latitude']
        self.longitude = data['longitude']
        self.Ville = data['Ville']
        self.CodePostale = data['CodePostale']
        self.Departement = data['Departement']
        self.Region = data['Region']
        self.Close = data['Close']
        self.Open = data['Open']
        self.validFrom = data['validFrom']
        self.validThrough = data['validThrough']

    def to_dict(self):
        return self.__dict__

def insert_Poi(Poi):
    # Connexion à MongoDB
    client = MongoClient('mongodb://localhost:27017/')

    # Sélection de la base de données et de la collection
    db = client['Poi']
    collection = db['poi']

    # Insertion de l'objet Store dans la collection
    collection.insert_one(Poi.to_dict())

    # Fermeture de la connexion à MongoDB
    client.close()


# test

# Données du Poi
data = {
    '_id': '6466098389eef1f9ee8bc920',
    'id': 'https://data.datatourisme.fr/13/000fac17-cff9-3918-a3d6-8edc919c8533',
    'type': 'Store',
    'lastUpdate': '2022-08-11',
    'email': ['calvijet@gmail.com'],
    'telephone': ['+33 6 26 17 04 97'],
    'typeContact': ['foaf:Agent', 'Agent'],
    'homepage': ['https://www.calvi-jet.fr/'],
    'Description': 'Lors de vos vacances en corse, les amateurs de sports nautiques et de …',
    'latitude': 42.555104,
    'longitude': 8.761533,
    'Ville': 'Calvi',
    'CodePostale': 20260,
    'Departement': 'Haute-Corse',
    'Region': 'Corse',
    'Close': '20:30:00',
    'Open': '08:00:00',
    'validFrom': '2023-05-01T00:00:00',
    'validThrough': '2023-10-31T23:59:59'
}

# Création de l'objet Poi
Poi = Poi(data)

# Insertion du poi dans MongoDB
insert_Poi(Poi)
