import pandas as pd
import json

objects_path = '/app/Data/JSON/objects/'
index_path = '/app/Data/JSON/index.json'

with open(index_path) as json_data:
    index = json.load(json_data)

def dataframeFromJson(objects_path, index_path):
    listOfPathJson = []
    
    for obj in index:
        listOfPathJson.append(objects_path + obj['file'])
        
    listOfJson = []
    
    for json_path in listOfPathJson:
        with open(json_path) as json_data:
            jsonObject = json.load(json_data)
            listOfJson.append(jsonObject)
    
    col_select_raw = [
    '@id',
    'rdfs:label.fr',
    '@type',
    'hasContact',
    'hasDescription',
    'hasTheme',
    'isLocatedAt',
    'lastUpdate'
    ]
    
    df = pd.json_normalize(listOfJson, errors='ignore')[col_select_raw]
    
    clean_name = {
        '@id': 'id',
        'rdfs:label.fr': 'nom',
        '@type': 'type',
        'hasContact': 'contact',
        'hasDescription': 'description',
        'hasTheme': 'theme',
        'isLocatedAt': 'location',
        'lastUpdate': 'maj'
    }
    
    return df.rename(columns=clean_name)


def preprocessData(df):
    df_preprocessed = df.copy()
    
    # Nom
    df_preprocessed['nom'] = df_preprocessed['nom'].map(lambda x: x[0])
    
    # Type
    def prepoType(types):
        if types[-1] == "PointOfInterest" and types[-2] != "PlaceOfInterest":
            return types[-2]
        elif types[-1] == "PointOfInterest" and types[-2] == "PlaceOfInterest":
            return types[-3]
        else:
            return types[-1]
        
        
    df_preprocessed['type'] = df_preprocessed['type'].map(lambda x: prepoType(x))
    
    replace_type_dict = {
    "HolidayResort": "Accommodation",
    "SportsCompetition": "SportsAndLeisurePlace",
    "CampingAndCaravanning": "Accommodation",
    "HotelTrade": "Accommodation",
    "SwimmingPool": "SportsAndLeisurePlace",
    "LodgingBusiness": "Accommodation",
    "WalkingTour": "Activity",
    "ZooAnimalPark": "Activity",
    "Tour": "Activity",
    "TastingProvider": "FoodEstablishment",
    "ReligiousSite": "PlaceToSee",
    "EntertainmentAndEvent": "Activity",
    "District": "PlaceToSee",
    "SquashCourt": "SportsAndLeisurePlace",
    "ThemePark": "Activity",
    "TechnicalHeritage": "PlaceToSee",
    "ParkAndGarden": "PlaceToSee",
    "CollectiveAccommodation": "Accommodation",
    "Ruins": "PlaceToSee",
    "TennisComplex": "SportsAndLeisurePlace",
    "DefenceSite": "PlaceToSee",
    "TouristTrain": "Transport",
    "Transporter": "Transport",
    "CulturalSite": "PlaceToSee",
    "Restaurant": "FoodEstablishment",
    "Museum": "PlaceToSee"
}
    df_preprocessed['type2'] = df_preprocessed['type'].replace(replace_type_dict)
    
    # Contact
    df_preprocessed['contactId'] = df_preprocessed['contact']\
    .map(lambda x: x[0]['@id'] if type(x) != float else None)
    
    df_contact = pd.DataFrame()
    
    for el in df['contact']:
        if type(el) != float:
            df_contact = pd.concat([df_contact, pd.json_normalize(el[0])])
    
    df_contact.set_index("@id", inplace=True)
    
    df_preprocessed = df_preprocessed.join(df_contact, on='contactId', how='left') \
               .drop_duplicates(subset='id') \
               .drop(columns=['contactId', 'contact', '@type'])
    
    df_preprocessed = df_preprocessed.rename(columns={
        'schema:email': 'email',
        'schema:telephone': 'telephone',
        'foaf:homepage': 'homepage'
    })
    
    df_preprocessed[['email', 'telephone', 'homepage']] = \
    df_preprocessed[['email', 'telephone', 'homepage']]\
    .applymap(lambda x: x[0] if type(x) != float else None)
    
    # Description
    df_preprocessed['description'] = \
    df_preprocessed['description']\
    .map(lambda x: x[0]["shortDescription"]["fr"][0] if type(x) != float else None)
    
    # Theme unique
    df_theme = pd.DataFrame()
    
    for el in df_preprocessed['theme']:
        if type(el) != float:
            df_theme = pd.concat([df_theme, pd.json_normalize(el)]).drop_duplicates(['@id'])
            
    df_theme_unique = df_theme.set_index("@id")[['@type', 'rdfs:label.fr']]
    df_theme_unique = df_theme_unique.rename(columns={
        '@type': 'typeTheme',
        'rdfs:label.fr': 'nomTheme'
    })
    df_theme_unique[['typeTheme', 'nomTheme']] = \
    df_theme_unique[['typeTheme', 'nomTheme']]\
    .applymap(lambda x: x[0] if type(x) != float else None)
    
    # Theme
    df_theme = df_preprocessed[['id', 'theme']].copy()
    
    df_theme['theme'] = df_theme['theme']\
    .map(lambda x: [el['@id'] for el in x] if type(x) != float else None)
    
    df_theme = df_theme.explode('theme')
    
    # Location
    df_location = pd.DataFrame()
    
    for el in df_preprocessed['location']:
        if type(el) != float:
            df_location = pd.concat([df_location, pd.json_normalize(el[0])])
    
    df_location = df_location.set_index("@id")
    
    d ={"id_adresse": [],
    "Ville": [],
    "CodePostale": [],
    "Departement": [],
    "Region": []}

    for el in df_location['schema:address']:
        id_adresse = el[0]['@id']
        ville = el[0]['schema:addressLocality']
        cp = el[0]['schema:postalCode']
        dep = el[0]['hasAddressCity']['isPartOfDepartment']['rdfs:label']['fr']
        reg = el[0]['hasAddressCity']['isPartOfDepartment']['isPartOfRegion']['rdfs:label']['fr']
        d['id_adresse'].append(id_adresse)
        d['Ville'].append(ville)
        d['CodePostale'].append(cp)
        d['Departement'].append(dep[0])
        d['Region'].append(reg[0])
        
    df_adresse = pd.DataFrame(d).set_index("id_adresse")
    df_location['id_adresse'] = df_location['schema:address'].map(lambda x: x[0]['@id'])
    df_location = df_location.join(df_adresse, how='left', on='id_adresse')
    
    d ={"id_opening": [],
    "Close": [],
    "Open": [],
    "validFrom": [],
    "validThrough": []}

    for el in df_location['schema:openingHoursSpecification']:
        id_opening = el[0]['@id']
        try:
            Close = el[0]['schema:closes']
        except:
            Close = None
        try:
            Open = el[0]['schema:opens']
        except:
            Open = None
        try:
            validFrom = el[0]['schema:validFrom']
        except:
            validFrom = None
        try:
            validThrough = el[0]['schema:validThrough']
        except:
            validThrough = None
        d['id_opening'].append(id_opening)
        d['Close'].append(Close)
        d['Open'].append(Open)
        d['validFrom'].append(validFrom)
        d['validThrough'].append(validThrough)
        
    df_opening = pd.DataFrame(d).set_index("id_opening")
    df_location['id_opening'] = df_location['schema:openingHoursSpecification'].map(lambda x: x[0]['@id'])
    df_location = df_location.join(df_opening, how='left', on='id_opening')[[
    "schema:geo.schema:latitude",
    "schema:geo.schema:longitude",
    "Ville",
    "CodePostale",
    "Departement",
    "Region",
    "Close",
    "Open",
    "validFrom",
    "validThrough",
]]
    
    df_preprocessed['location'] = df_preprocessed['location'].map(lambda x: x[0]['@id'])
    df_preprocessed = df_preprocessed.join(df_location, on='location', how='left') \
               .drop_duplicates(subset='id') \
               .drop(columns=['location'])
    
    df_preprocessed = df_preprocessed.rename(columns={
    'schema:geo.schema:latitude': 'latitude',
    'schema:geo.schema:longitude': 'longitude'
})
    
    df_preprocessed[['latitude', 'longitude']] = \
    df_preprocessed[['latitude', 'longitude']].astype(float)
    
    return df_preprocessed, df_theme_unique, df_theme


def main():
    df_raw = dataframeFromJson(objects_path, index_path)
    df_preprocessed, df_theme_unique, df_theme = preprocessData(df_raw)
    df_preprocessed.to_csv("/app/Data/POI.csv")
    df_theme.to_csv("/app/Data/theme.csv")
    df_theme_unique.to_csv("/app/Data/theme_unique.csv")

if __name__ == "__main__":
    main()