from param import default_database, database, user, password, host, port
from param import path_POI_csv, path_theme_csv, path_theme_unique_csv
from param import struct_table_POI, struct_table_theme_unique, struct_table_theme

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import psycopg2
import pandas as pd 
import csv


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


class BDDR:

    def __init__(self, database : str = default_database):
        self.ConnectDB(database)
        

    def ConnectDB(self, database : str, user : str = user, password : str = password, host : str = host, port : str = port):

        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port

        try:
            self.connection = psycopg2.connect(
                                    database = self.database, 
                                    user = self.user, 
                                    password = self.password, 
                                    host = self.host, 
                                    port = self.port
                                    )
            
            # Commit dans la base de donnée à chaque exécution d'actions
            self.connection.autocommit = True
            self.cursor = self.connection.cursor()

            print("Connection to the Database '{}' is successfull.".format(database))

        except Exception as e:
            print("Cannot connect to Database : '{}'.".format(database))
            print(e)
    

    def close(self):
        self.connection.close()


    def info(self):

        list_database = [db[0] for db in self.query("SELECT datname FROM pg_database;")]
        list_table = [tb[0] for tb in self.query("SELECT relname FROM pg_class WHERE relkind='r' AND relname !~ '^(pg_|sql_)';")]
        
        print("""
        ########## Info Connection ##########
        Database : {database}
        user : {user}
        password : {password}
        host : {host}
        port : {port}\n
        Databases : {list_database}
        Tables : {list_table}
        #####################################
        """.format(
            database = self.database,
            user = self.user,
            password = "*" * len(self.password),
            host = self.host,
            port = self.port,
            list_database = list_database,
            list_table = list_table
            ))


    def query(self, sql_query):

        try:
            self.cursor.execute(sql_query)
            try:
                return self.cursor.fetchall()
            except:
                return None

        except Exception as e:
            print("Cannot execute query : '{}'.".format(sql_query))
            print(e)

    
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
    print("start")
    BDDR1 = BDDR()

    BDDR1.query("DROP DATABASE itinerairedevoyage;")
    BDDR1.info()

    BDDR1.query("CREATE DATABASE itinerairedevoyage;")
    BDDR1.ConnectDB(database)

    BDDR1.query(struct_table_POI)
    BDDR1.query(struct_table_theme_unique)
    BDDR1.query(struct_table_theme)

    BDDR1.info()

    BDDR1.insert_df("poi", path_POI_csv, True)
    BDDR1.insert_df("themeunique", path_theme_unique_csv, True)
    BDDR1.insert_df("theme", path_theme_csv, True)

    print(BDDR1.query("SELECT * FROM poi LIMIT 10;"))
