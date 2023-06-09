from param import database
from param import path_POI_csv, path_theme_csv, path_theme_unique_csv
from param import struct_table_POI, struct_table_theme_unique, struct_table_theme
from postgres import BDDR


BDDR1 = BDDR()

#BDDR1.query("DROP DATABASE itinerairedevoyage;")
#BDDR1.info()

BDDR1.query("CREATE DATABASE {db};".format(db = database))
BDDR1.ConnectDB(database)

BDDR1.query(struct_table_POI)
BDDR1.query(struct_table_theme_unique)
BDDR1.query(struct_table_theme)

BDDR1.info()

BDDR1.insert_df("poi", path_POI_csv, True)
BDDR1.insert_df("themeunique", path_theme_unique_csv, True)
BDDR1.insert_df("theme", path_theme_csv, True)

BDDR1.close()
print(BDDR1.query("SELECT * FROM poi LIMIT 2;"))