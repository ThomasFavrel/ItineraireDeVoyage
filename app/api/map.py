import folium
import webbrowser
import pandas as pd
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

# Enlever la condition suivante pour l'utiliser dans un Notebook
if __name__ == "__main__":
  # Récupère les informations sur les POI dans un DataFrame
  df_POI = pd.read_csv("./Data/POI.csv")

  idv = Map() # (42.143016, 9.104581)
  # Ajoute les marqueurs des POIs et 
  idv.marker(df_POI)
  #idv.circle(42.143016, 9.104581, 100)

  idv.my_map
  #itv.showMap()
