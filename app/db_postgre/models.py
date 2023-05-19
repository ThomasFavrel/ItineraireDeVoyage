from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import psycopg2
import pandas as pd 
import csv

# Constantes
database = "itinerairevoyage"
user = "postgres"
password = "0000"
host = "localhost"
port = "5432"

# Chemins
path_data = "./Data/"
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


class Postgres:

    def __init__(self, user : str = user, password : str = password):

        try:
            self.conn = psycopg2.connect("user={user} password='{password}'".format(user = user, password = password))
            
            # Commit dans la base de donnée à chaque exécution d'actions
            self.con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cursor = self.con.cursor()
            print("Connection to PostgreSQL's user '{}' is successfull.".format(user))

        except Exception as e:
            print("Cannot connect to PostgreSQL's user : {}.".format(user))
            print(e)
    

    def CreateDatabase(self, name_db : str):

        sql_create_db = "create database " + name_db + ";"

        try:
            self.cursor.execute(sql_create_db)
            print("Database '{}' has been successfully created".format(name_db))

        except Exception as e:
            print("Cannot create Database.")
            print(e)


class BDDR:

    def __init__(self, database : str, user : str = user, password : str = password, host : str = host, port : str = port):

        self.database = database
        print(self.database, user, password, host, port)

        try:
            self.conn = psycopg2.connect(
                                    database = self.database, 
                                    user = user, 
                                    password = password, 
                                    host = host, 
                                    port = port
                                    )
            
            # Commit dans la base de donnée à chaque exécution d'actions
            self.conn.autocommit = True
            print("Connection to the Database '{}' is successfull.".format(database))

        except Exception as e:
            print("Cannot connect to Database : '{}'.".format(database))
            print(e)

        self.cursor = conn.cursor()
        
    
    def pp_table(self, table_name : str, table_path : str):
    
        self.cursor.execute("Select * FROM {} LIMIT 0".format(table_name))
        colnames = [desc[0] for desc in self.cursor.description]

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


    def info_bdd(self):

        print(self.database)


    def query(self, sql_query):

        try:
            self.cursor.execute(sql_query)

        except Exception as e:
            print("Cannot execute query : '{}'.", format(sql_query))
            print(e)
    

    def insert_csv(self, table_name : str, table_path : str):
        # A utiliser si pas besoin de pré-traitement

        self.pp_table(table_name, table_path)
        # Pour connaître le nombre de colonnes de la table
        self.query("Select * FROM {} LIMIT 0".format(table_name))
        colnames = [desc[0] for desc in self.cursor.description]
        insert_row = "INSERT INTO " + table_name + " VALUES (" + "%s, " * (len(colnames)-1)  + "%s);"
        
        with open(table_path, "r", encoding = "utf8") as f:
            reader = csv.reader(f)
            next(reader) # Skip the header row.

            for row in reader:    
                
                if len(tuple(row)) != len(colnames):
                    print("Cannot insert a {} tuple in {} columns.\nThey need to be the same size.".format(len(tuple(row)), len(colnames)))
                    break
                
                try:
                    self.query(insert_row % tuple(row))

                except Exception as e:
                    print("Cannot insert in table : '{}'.".format(table_name))
                    print(e)
    

    def insert_df(self, table_name : str, table_path : str, preprocess : bool = False):
        
        # Preprocess utile si il y a des valeurs vides ("" remplacé par "Null"), et l'utilisation de caractère "a'a"(remplacé par "'a''a'")
        # Enlève la première colonne de POI et corrige l'id de la table theme (redondance de clé)
        if preprocess:
            df = self.pp_table(table_name, table_path)
        else:
            df = pd.read_csv(table_path)
            
        self.query("Select * FROM {} LIMIT 0".format(table_name))
        colnames = [desc[0] for desc in self.cursor.description]
        insert_row = "INSERT INTO " + table_name + " VALUES (" + "%s, " * (len(colnames)-1)  + "%s);"
        
        x, y = df.shape

        for i in range(x):    
            
                row = df.loc[i]
                #print(tuple(row))
                if len(tuple(row)) != len(colnames):
                    print("Cannot insert a {} tuple in {} columns.\nThey need to be the same size.".format(len(tuple(row)), len(colnames)))
                    break
                
                try:
                    self.query(insert_row % tuple(row))

                except Exception as e:
                    print("Cannot insert in table : '{}'.".format(table_name))
                    print(e)


if __name__ == "__main__":
    # Création de l'objet Postgres
    Postgres_con = Postgres()
    # Création d'une base de donnée 
    Postgres_con.CreateDatabase("itinerairevoyage")

    # Création de l'objet BDDR
    BDD = BDDR("itinerairevoyage")

    # Supprime les tables
    BDD.query("DROP TABLE Theme;")
    BDD.query("DROP TABLE POI;")
    BDD.query("DROP TABLE ThemeUnique;")

    # Création des tables
    BDD.query(struct_table_POI)
    BDD.query(struct_table_theme_unique)
    BDD.query(struct_table_theme)
    # Insertion des données dans les tables depuis les fichiers csv
    BDD.insert_df("poi", path_POI_csv, True)
    BDD.insert_df("themeunique", path_theme_unique_csv, True)
    BDD.insert_df("theme", path_theme_csv, True)



