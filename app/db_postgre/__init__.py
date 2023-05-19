from models import Postgres
from models import BDDR

if __name__ == "__main__":
    # Création de l'objet Postgres
    Postgres_con = Postgres()
    # Création d'une base de donnée 
    Postgres_con.CreateDatabase("itinerairevoyage")

    # Création de l'objet BDDR
    BDD = BDDR("itinerairevoyage")
    # Création des tables
    BDD.query(struct_table_POI)
    BDD.query(struct_table_theme_unique)
    BDD.query(struct_table_theme)
    # Insertion des données dans les tables depuis les fichiers csv
    BDD.insert_df("poi", path_POI_csv, True)
    BDD.insert_df("themeunique", path_theme_unique_csv, True)
    BDD.insert_df("theme", path_theme_csv, True)