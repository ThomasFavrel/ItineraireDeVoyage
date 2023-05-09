from pymongo import MongoClient

class POI:
    def __init__(self, id, poi_type, last_update, emails, telephones, contact_types, homepage, description, latitude, longitude, city, postal_code, department, region, close, open, valid_from, valid_through):
        self.id = id
        self.poi_type = poi_type
        self.last_update = last_update
        self.emails = emails
        self.telephones = telephones
        self.contact_types = contact_types
        self.homepage = homepage
        self.description = description
        self.latitude = latitude
        self.longitude = longitude
        self.city = city
        self.postal_code = postal_code
        self.department = department
        self.region = region
        self.close = close
        self.open = open
        self.valid_from = valid_from
        self.valid_through = valid_through

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
