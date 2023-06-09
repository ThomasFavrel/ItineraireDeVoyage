# Connexion Database
default_database = "postgres"
database = "itinerairedevoyage"
user = "username"
password = "password"
host = "postgres"
port = "5432"


# Chemins
path_data = "./data/" 
path_POI_csv = path_data + "POI.csv"
path_theme_csv = path_data + "theme.csv"
path_theme_unique_csv = path_data + "theme_unique.csv"


# Structures des tables
struct_table_POI = """CREATE TABLE POI(
    id VARCHAR PRIMARY KEY,
    nom VARCHAR,
    type VARCHAR,
    description VARCHAR,
    theme VARCHAR,
    lastupdate DATE,
    type2 VARCHAR,
    email VARCHAR,
    telephone VARCHAR,
    homepage VARCHAR,
    latitude FLOAT,
    longitude FLOAT,
    ville VARCHAR,
    codePostale INTEGER,
    departement VARCHAR,
    region VARCHAR,
    close TIME,
    open TIME,
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

