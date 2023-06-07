from pymongo import MongoClient

from mongoengine import Document, StringField, DateTimeField, ListField, URLField, FloatField

class POI(Document):
    # id = StringField(required=False)
    type = StringField()
    lastUpdate = DateTimeField()
    email = ListField(StringField())
    telephone = ListField(StringField())
    typeContact = ListField(StringField())
    homepage = ListField(StringField())
    Description = StringField()
    latitude = FloatField()
    longitude = FloatField()
    Ville = StringField()
    CodePostale = StringField()
    Departement = StringField()
    Region = StringField()
    Close = StringField()
    Open = StringField()
    validFrom = DateTimeField()
    validThrough = DateTimeField()

    meta = {
        'collection': 'POI'
    }


class ThemeUnique:
    def __init__(self, id: str, type: str, label_fr: str):
        self.id = id
        self.type = type
        self.label_fr = label_fr
                
class Theme:
    def __init__(self, id, type, label_de, label_pt, label_en, label_it, label_fr, label_nl, label_es):
        self.id = id
        self.type = type
        self.label_de = label_de
        self.label_pt = label_pt
        self.label_en = label_en
        self.label_it = label_it
        self.label_fr = label_fr
        self.label_nl = label_nl
        self.label_es = label_es

class MongoDB:
    def __init__(self, host, port, db_name):
        self.client = MongoClient(host, port)
        self.db = self.client[db_name]
        self.poi_collection = self.db["db_mongo"]

    def add_poi(self, poi):
        poi_dict = {
            "id": poi.id,
            "type": poi.poi_type,
            "lastUpdate": poi.last_update,
            "schema:email": poi.emails,
            "schema:telephone": poi.telephones,
            "typeContact": poi.contact_types,
            "foaf:homepage": poi.homepage,
            "Description": poi.description,
            "schema:geo.schema:latitude": poi.latitude,
            "schema:geo.schema:longitude": poi.longitude,
            "Ville": poi.city,
            "CodePostale": poi.postal_code,
            "Departement": poi.department,
            "Region": poi.region,
            "Close": poi.close,
            "Open": poi.open,
            "validFrom": poi.valid_from,
            "validThrough": poi.valid_through
        }
        self.poi_collection.insert_one(poi_dict)
