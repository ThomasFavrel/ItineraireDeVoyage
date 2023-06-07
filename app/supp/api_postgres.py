from fastapi import FastAPI
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import psycopg2
import pandas as pd 
import csv
import time

# Constantes
default_database = "postgres" 
database = "itinerairevoyage"
user = "username"
password = "password"
host = "localhost"
port = "5432"


# Chemins
path_data = "../../Data/" #"./Data/"
path_POI_csv = path_data + "POI.csv"
path_theme_csv = path_data + "theme.csv"
path_theme_unique_csv = path_data + "theme_unique.csv"


# Structures des tables
struct_table_POI = """CREATE TABLE POI(
    id VARCHAR PRIMARY KEY,
    type VARCHAR,
    lastUpdate DATE,
    email VARCHAR,
    telephone VARCHAR,
    typeContact VARCHAR,
    homepage VARCHAR,
    Description VARCHAR,
    latitude FLOAT,
    longitude FLOAT,
    Ville VARCHAR,
    CodePostale INTEGER,
    Departement VARCHAR,
    Region VARCHAR,
    Close TIME,
    Open TIME,
    validFrom VARCHAR,
    validThrough VARCHAR
);"""

struct_table_theme_unique = """CREATE TABLE ThemeUnique(
    id VARCHAR PRIMARY KEY,
    type VARCHAR,
    fr VARCHAR
);"""

struct_table_theme = """CREATE TABLE Theme(
    id VARCHAR PRIMARY KEY,
    poi_id VARCHAR,
    theme_id VARCHAR,
    FOREIGN KEY (poi_id) REFERENCES POI(id),
    FOREIGN KEY (theme_id) REFERENCES ThemeUnique(id)
);"""

#@api.get("/query")
def query(sql_query: str):
    
    try:
        cursor.execute(sql_query)
        try:
            return {
            'data': cursor.fetchall()
            }
        except:
            return "Operation successfull."
    except Exception as e:
        print("Cannot execute query : '{}'.", format(sql_query))
        print(e)


#@api.get("/{db: str}")
def ConnectDB(database: str, user: str, password: str, host: str, port: int):
    global cursor
    global conn
    try:
        conn = psycopg2.connect(
                                database = database, 
                                user = user, 
                                password = password, 
                                host = host, 
                                port = port
                                )
        
        # Commit dans la base de donnée à chaque exécution d'actions
        conn.autocommit = True
        print("Connection to the Database '{}' is successfull.".format(database))

    except Exception as e:
        print("Cannot connect to Database : '{}'.".format(database))
        print(e)

    cursor = conn.cursor()


#@api.get("/{db: str}")
def CreateDatabase(name_db: str):

    sql_create_db = "CREATE DATABASE " + name_db + ";"

    try:
        query(sql_create_db)
        print("Database '{}' has been successfully created.".format(name_db))

    except Exception as e:
        print("Cannot create Database.")
        print(e)

#@api.get("/{db: str}")
def DeleteDatabase(name_db: str):

    sql_delete_db = "DROP DATABASE " + name_db + ";"

    try:
        query(sql_delete_db)
        print("Database '{}' has been successfully deleted.".format(name_db))

    except Exception as e:
        print("Cannot delete Database.")
        print(e)


#@api.get("/{tb: str}")
def DeleteTable(name_tb: str):

    sql_delete_tb = "DROP TABLE " + name_tb + ";"

    try:
        query(sql_delete_tb)
        print("Table '{}' has been successfully created".format(name_db))

    except Exception as e:
        print("Cannot delete Table.")
        print(e)


def pp_char(row):
    for i, cell in enumerate(row):
        if cell == "":
            row[i] = "Null"
        else:
            row[i] = "'" + cell.replace("'", "''") + "'"
    return row

def pp_col(table_name, row, count):
    if table_name == "poi": # La première colonne n'est pas pris en compte dans la structure de la table
        row = row[1:]
    elif table_name == "theme": # Le fichier csv contient un colone remplie de chiffre (id) contenant des doublons
        row[0] = count
    return row

def pp_table(table_name : str, table_path : str):
    
        cursor.execute("Select * FROM {} LIMIT 0".format(table_name))
        colnames = [desc[0] for desc in cursor.description]

        df = pd.DataFrame(columns = colnames)
        
        with open(table_path, "r", encoding = "utf8") as f:
                reader = csv.reader(f)
                next(reader) # Skip the header row.
                count = 0
                for i, row in enumerate(reader):    
                    row = pp_char(row)
                    row = pp_col(table_name, row, count)
                    count += 1  
                    df.loc[i] = row
        
        # df.to_csv(table_path, sep=',', encoding='utf-8')
        return (df)


#@api.post("/insert/df")
def insert_df(table_name: str, table_path: str, preprocess: bool = False):
        
    # Preprocess utile si il y a des valeurs vides ("" remplacé par "Null"), et l'utilisation de caractère "a'a"(remplacé par "'a''a'")
    # Enlève la première colonne de POI et corrige l'id de la table theme (redondance de clé)
    if preprocess:
        df = pp_table(table_name, table_path)
    else:
        df = pd.read_csv(table_path)
        
    query("Select * FROM {} LIMIT 0".format(table_name))
    colnames = [desc[0] for desc in cursor.description]
    insert_row = "INSERT INTO " + table_name + " VALUES (" + "%s, " * (len(colnames)-1)  + "%s);"
    
    x, y = df.shape

    for i in range(x):    
        
            row = df.loc[i]
            #print(tuple(row))
            if len(tuple(row)) != len(colnames):
                print("Cannot insert a {} tuple in {} columns.\nThey need to be the same size.".format(len(tuple(row)), len(colnames)))
                break
            
            try:
                query(insert_row % tuple(row))

            except Exception as e:
                print("Cannot insert in table : '{}'.".format(table_name))
                print(e)

#@api.post("/insert/row")
def InsertRow(list_in, columns = None):
    print("cool")

#@api.post("/insert/row")
def DeleteRow(list_out):
    print("cool")

#@api.get("/select")
def SelectRow():
    print("ok")

#@api.get("/sample")
def sample(table: str, n: str):
    sql_sample = "SELECT * FROM " + table + " LIMIT " + n + ";"

    try:
        sample = query(sql_sample)
        return sample

    except Exception as e:
        print("Cannot give sample.")
        print(e)



ConnectDB(default_database, user, password, host, port)
DeleteDatabase(database)

CreateDatabase(database)
ConnectDB(database, user, password, host, port)

# Création des tables
query(struct_table_POI)
query(struct_table_theme_unique)
query(struct_table_theme)

print(query("SELECT datname FROM pg_database;"))
print(query("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';"))

# Insertion des données depuis les fichiers csv
insert_df("poi", path_POI_csv, True)
insert_df("themeunique", path_theme_unique_csv, True)
insert_df("theme", path_theme_csv, True)

#
print(sample("poi", "20"))


import folium
import webbrowser
import pandas as pd
import pandas.io.sql as psql
from random import randint
import ast

### Ajouter le nom des POIs dans le csv

# Documentation folium : https://python-visualization.github.io/folium/modules.html#module-folium.map
# Liste Icone : https://fontawesome.com/search?m=free&o=r
"""Color :
'beige', 'gray', 'lightgray', 'darkpurple', 'orange', 'darkblue', 'black', 'purple', 'green', 'darkred', 'red', 
'lightred', 'lightgreen', 'blue', 'darkgreen', 'pink', 'cadetblue', 'lightblue', 'white'
"""

# dictionnaire des catégories de type (les couleurs seront supprimer pour être utilisé pour différencier les jours)
dict_ctg_POI = {
    "Store" : {"color" : "pink", "icon" :  "store", "icon_color" : "red"},
    "CulturalSite" : {"color" : "blue", "icon" :  "building-columns", "icon_color" : "white"},
    "HotelTrade" : {"color" : "green", "icon" :  "hotel", "icon_color" : "white"},
}

# Il faudra mieux changer la couleur selon les jours et pas selon le type de POI
def random_color(n):
    # Pour obtenir une couleur aléatoire (pas unique) pour chaque jour
    list_colors = []
    for i in range(n):
        list_colors.append('#%06X' % randint(0, 0xFFFFFF))
    return list_colors


class Map:    
    
    def __init__(self, zoom_start = 8, map_path = "map.html"):

        # Coordonnées limites de la carte (latitude, longitude)
        sw = (41.3149, 8.4045)
        ne = (43.2, 9.6899)
        
        # Création de la carte
        self.my_map = folium.Map(
            tiles='OpenStreetMap',
            location = None, 
            min_lat = sw[0], 
            max_lat = ne[0], 
            min_lon = sw[1], 
            max_lon = ne[1], 
            max_bounds = [sw, ne],
            zoom_start = zoom_start,
            min_zoom = 8,
            max_zoom = 18
        )

        # Sauvegarde la carte
        self.map_path = map_path
        self.my_map.save(self.map_path)
        
        # Affiche les coordonnées GPS avec un clique sur la carte
        #self.my_map.add_child(folium.LatLngPopup())
    
    
    def showMap(self):
        # Ouvre la carte enregistré dans une page web
        webbrowser.open(self.map_path)
    
    
    def str_to_list(self, string):
        try: 
            return ast.literal_eval(string)[0]
        except:
            return "https://www.google.com/"
        
    
    def marker(self, df): # df_coord
        # Marque tous les POIs sur la carte 
        # "df" doit être composé des colonnes : latitude, longitude, type, name (à ajouter), id, homepage, telephone, email

        for index, poi in df.iterrows():
            if poi["type"] in list(dict_ctg_POI.keys()):
                color = dict_ctg_POI[poi["type"]]["color"]
                icon = dict_ctg_POI[poi["type"]]["icon"]
                icon_color = dict_ctg_POI[poi["type"]]["icon_color"]
            else:
                color = "lightgray"
                icon = "fa-solid fa-question"
                icon_color = "white"
                
            folium.Marker(
                location = [poi["latitude"], poi["longitude"]], 
                popup='<a href="{url}" target="_blank">{text}</a>\n{email}\n{phone}'.format(
                    url = self.str_to_list(poi["homepage"]), 
                    text = poi["type"],
                    email = self.str_to_list(poi["email"]),
                    phone = self.str_to_list(poi["telephone"]),
                ), 
                icon = folium.Icon(
                    color = color, 
                    icon = icon, 
                    icon_color = icon_color,
                    prefix = "fa"
                ), 
                tooltip = "Click for more info",
            ).add_to(self.my_map)

        
    def circle(self, lat, long, radius):
        # Affiche un rayon (utile pour la distance maximum par jour ou autres informations)
        
        folium.Circle(
            location = [lat, long],
            radius = radius,
            popup = "",
            stroke = False,
            color = "#3186cc",
            opacity = "0.7",
            fill = True,
            fill_opacity = "0.3",
            fill_color = "#3186cc"
        ).add_to(self.my_map)


def map():
    # Récupère les informations sur les POI dans un DataFrame
    #df_POI = pd.read_csv("./Data/POI.csv")
    cursor.execute('SELECT * FROM poi')
    tuples_list = cursor.fetchall()
    query("Select * FROM {} LIMIT 0".format("poi"))
    colnames = [desc[0] for desc in cursor.description]

    df_POI = pd.DataFrame(tuples_list, columns=colnames)
    #df_POI = pd.read_sql_query("select * from poi;" ,conn)

    idv = Map() # (42.143016, 9.104581)

    # Ajoute les marqueurs des POIs et 
    idv.marker(df_POI)

    idv.showMap()

#map()