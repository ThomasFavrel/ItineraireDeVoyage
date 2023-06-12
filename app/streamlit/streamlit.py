import streamlit as st
import pandas as pd
import folium
import json
from streamlit_folium import st_folium
from pyroutelib3 import Router
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from sklearn.neighbors import NearestNeighbors
from sklearn.neighbors import KNeighborsRegressor
from geopy.geocoders import Nominatim
from random import randint
import ast
import requests

APP_TITLE = "Itinéraire de vacances 🏁"
APP_SUBTITLE = 'Itinéraire de vacances 🏁'

#df = pd.read_csv("/app/Data/POI.csv")



dict_ctg_POI = {
    "Store" : {"color" : "red", "icon" :  "euro", "icon_color" : "white"},
    "SportsAndLeisurePlace" : {"color" : "blue", "icon" :  "soccer-ball-o", "icon_color" : "white"},
    "TouristInformationCenter" : {"color" : "green", "icon" :  "info", "icon_color" : "white"},
    "SportsEvent" : {"color" : "beige", "icon" :  "futbol-o", "icon_color" : "white"},
    "CulturalSite" : {"color" : "orange", "icon" :  "institution", "icon_color" : "white"},
    "HotelTrade" : {"color" : "purple", "icon" :  "hotel", "icon_color" : "white"},
    "FoodEstablishment" : {"color" : "lightred", "icon" :  "cutlery", "icon_color" : "white"},
    "Restaurant" : {"color" : "lightred", "icon" :  "cutlery", "icon_color" : "white"},
    "ThemePark" : {"color" : "lightblue", "icon" :  "trophy", "icon_color" : "white"},
    "Ruins" : {"color" : "cadetblue", "icon" :  "diamond", "icon_color" : "white"},
    "Museum" : {"color" : "cadetblue", "icon" :  "bank", "icon_color" : "white"}
}

class NoRoute(Exception):
    pass


@st.cache_resource
def calcul_distance(point1: tuple, point2: tuple, moyenLocomtion: str):
    router = Router(moyenLocomtion)
    p1 = router.findNode(*point1)
    p2 = router.findNode(*point2)
    status, route = router.doRoute(p1, p2)
    
    if status == "success":
        route_latLon = list(map(router.nodeLatLon, route))
        total_distance = 0
        
        for i in range(len(route_latLon) - 1):
            current_coord = route_latLon[i]
            next_coord = route_latLon[i + 1]
            dist = router.distance(current_coord, next_coord)
            total_distance += dist
        return total_distance
    
    else:
        return("Pas de route trouvé ...")

@st.cache_resource 
def itineraire_villes(moyenLocomtion: str, *coordonneesHotels: tuple):
    router = Router(moyenLocomtion)
    listePoints = []
    listeCoordo = [coordo for coordo in coordonneesHotels]
    
    for hotel in coordonneesHotels:
        listePoints.append(router.findNode(*hotel))
        
    nombreVilles = len(listePoints)
    matriceDistance = [[0] * nombreVilles for _ in range(nombreVilles)]
    
    for i in range(nombreVilles):
        for j in range(i+1, nombreVilles):
            matriceDistance[i][j] = calcul_distance(listeCoordo[i],
                                                    listeCoordo[j],
                                                    moyenLocomtion)
    
    manager = pywrapcp.RoutingIndexManager(len(matriceDistance), 1, 0)
    routing = pywrapcp.RoutingModel(manager)
    
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return matriceDistance[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
     
    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)
    
    plan_output = []
    index = routing.Start(0)
    
    while not routing.IsEnd(index):
        plan_output.append(manager.IndexToNode(index))
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        
    plan_output.append(manager.IndexToNode(index))
    return plan_output

def str_to_list(string):
        try: 
            return ast.literal_eval(string)[0]
        except:
            return "https://www.google.com/"

@st.cache_resource
def print_map(moyenLocomtion: str, coordonneesHotels, df, hotelcoord):
    router = Router(moyenLocomtion)
    listePoints = []
    listeCoord = []

    for hotel in coordonneesHotels:
        listePoints.append(router.findNode(*hotel))
        listeCoord.append(hotel)
    optmizePlan = itineraire_villes(moyenLocomtion, *listeCoord)

    sw = (41.3149, 8.4045)
    ne = (43.2, 9.6899)

    m = folium.Map(
                    location=(router.nodeLatLon(listePoints[0])),
                    tiles='OpenStreetMap',
                    min_lat = sw[0], 
                    max_lat = ne[0], 
                    min_lon = sw[1], 
                    max_lon = ne[1], 
                    max_bounds = [sw, ne],
                    zoom_start = 16,
                    min_zoom = 8,
                    max_zoom = 18
                    )
    
    for index in range(len(listePoints)):
        start = listePoints[optmizePlan[index]]
        end = listePoints[optmizePlan[index + 1]]
        status, route = router.doRoute(start, end)
        
        if status != 'success':
            raise NoRoute

        route_latLon = list(map(router.nodeLatLon, route))

        
        folium.PolyLine(route_latLon, weight=5, opacity=.4).add_to(m)

        loca = router.nodeLatLon(start)
        if index < 1:
            #poi = pd.DataFrame([[loca[0], loca[1], "HotelTrade", "Hotel", None, None, None]], columns=['latitude', 'longitude', "type", "nom", "homepage", "email", "telephone"])
            poi = df.loc[(df['latitude'] == hotelcoord[0]) & (df['longitude'] == hotelcoord[1])]
        else:
            poi = df.loc[(df['latitude'] == listeCoord[index][0]) & (df['longitude'] == listeCoord[index][1])]
        print(poi.loc[:, ['latitude', 'longitude', "type", "nom", "homepage", "email", "telephone"]])
        if poi["type"].iloc[0] in list(dict_ctg_POI.keys()):
            color = dict_ctg_POI[poi["type"].iloc[0]]["color"]
            icon = dict_ctg_POI[poi["type"].iloc[0]]["icon"]
            icon_color = dict_ctg_POI[poi["type"].iloc[0]]["icon_color"]
            print(color, icon, icon_color)
        else:
            color = "lightgray"
            icon = "fa-solid fa-question"
            icon_color = "white"
        
        if poi['homepage'].iloc[0]:
            folium.Marker(
                location = loca, 
                popup='<a href="{url}" target="_blank">{text}</a>\n{email}\n{phone}'.format(
                    url = poi["homepage"].iloc[0], 
                    text = poi["nom"].iloc[0],
                    email = poi["email"].iloc[0],
                    phone = poi["telephone"].iloc[0]
                ), 
                icon = folium.Icon(
                    color = color,
                    icon = icon, 
                    prefix = "fa"
                ), 
                tooltip = "Click for more info",
            ).add_to(m)
        
        else:
            folium.Marker(
                location = loca, 
                popup='{text}\n{email}\n{phone}'.format(
                    text = poi["nom"].iloc[0],
                    email = poi["email"].iloc[0],
                    phone = poi["telephone"].iloc[0]
                ), 
                icon = folium.Icon(
                    color = color,
                    icon = icon, 
                    prefix = "fa"
                ), 
                tooltip = "Click for more info",
            ).add_to(m)

    
    return m

@st.cache_resource
def find_iti_POI(hotel: tuple,
                 types: list,
                 max_poi,
                 algo,
                 df):
    
    data = df[df['type'].isin(types)][['latitude', 'longitude']]
    
    if algo == "NN":
        knn = NearestNeighbors(n_neighbors=max_poi)
        knn.fit(data)
        dist, indices = knn.kneighbors([hotel])
        indices = list(indices[0])
        df_POI_selected = data.iloc[indices]
        coordo_POI = list(map(lambda x: tuple(x),
                              df_POI_selected[['latitude', 'longitude']].values)) 
        return coordo_POI

@st.cache_resource(experimental_allow_widgets=True)
def appOneDay(types: list, ville: str, modeTransport: str, maxPoi: int, df):
    latVille, lonVille = find_coord(ville)
    
    if df[(df["Ville"] == ville) & \
          (df["type2"] == "Accommodation")].shape[0] > 0:
        df_hotel = df[(df["Ville"] == ville) & \
          (df["type2"] == "Accommodation")].sample(1, random_state=1)
        latHotel, lonHotel = df_hotel.latitude.values[0], \
        df_hotel.longitude.values[0]
        
    # else:
    #     latHotel, lonHotel = knn.predict([[latVille, lonVille]])[0]
    
        
    listeCoordoneesPoi = find_iti_POI(hotel=(latHotel, lonHotel),
                                      types=types,
                                      max_poi=maxPoi,
                                      algo='NN',
                                      df=df)
    hotelcoord = (latHotel, lonHotel)
    total_coord = [(latVille, lonVille)] + listeCoordoneesPoi
    
    m = print_map(moyenLocomtion=modeTransport, coordonneesHotels=total_coord, df=df, hotelcoord = hotelcoord)
    # st_map = st_folium(m, width=700, height=450)
    return m


def find_coord(ville: str):
    geolocator = Nominatim(user_agent="my_geocoder")
    location = geolocator.geocode(ville)
    return location.latitude, location.longitude

# knnHotel = KNeighborsRegressor(n_neighbors=1)
# knnHotel.fit(df[df['type2'] == 'Accommodation'][['latitude', 'longitude']],
#              df[df['type2'] == 'Accommodation'][['latitude', 'longitude']])

@st.cache_resource(experimental_allow_widgets=True)
def request_api():
    requests.get('http://api:8000/init')
    requests.get('http://api:8000/connect')
    requests.get('http://api:8000/connectDB/db?database=itinerairedevoyage')
    request = requests.get('http://api:8000/read?table=poi')

    data = json.loads(request.content)
    # Va savoir pourquoi ma variable data est une liste de liste et pas un json
    df = pd.DataFrame(data, columns=["id", "nom", "type", "description", "theme", "maj", "type2", "email", "telephone", "homepage", "latitude", "longitude", "Ville", "CodePostale", "Departement", "Region", "Close", "Open", "validFrom", "validThough"])
    return df

def main():
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)
    df = request_api()

    # Choix des constantes

    # def update():
    #     st.session_state.submitted = True

    # st.sidebar.button('Valider', update)

    # st.sidebar.form_submit_button('Submit', on_click=update)

    # if st.session_state.submitted:
    #     st.write('Form submitted')

    # if 'submitted' not in st.session_state:
    #     st.session_state.submitted = False
    
    with st.form(key='my_form'):

        #  st.write(st.session_state.submitted)

        liste_ville = list(df.Ville.value_counts().index)
        # ville = st.sidebar.text_input('Ville')
        ville = st.sidebar.selectbox('Liste des villes', liste_ville)

        types_liste = (df[df['type2']!='Accommodation'].type.unique())
        types = st.sidebar.multiselect('Types', types_liste)

        transport_liste = ["À pied", "Voiture", "Cheval"]
        mode_transport = st.sidebar.selectbox('Moyen de transport', transport_liste)

        trad_transport = {
            "À pied": 'foot',
            "Voiture": 'car',
            "Cheval": 'horse'
        }

        max_poi = st.sidebar.selectbox('Nombre de visite', [x for x in range(3, 7)])

        submit_button = st.form_submit_button(label='Valider')
        

        if submit_button:
            m = appOneDay(types, ville, trad_transport[mode_transport], max_poi, df)
            st_map = st_folium(m, width=700, height=450)
            """
            try:
                m = appOneDay(types, ville, trad_transport[mode_transport], max_poi, df)
                st_map = st_folium(m, width=700, height=450)
            except NoRoute:
                st.caption('⚠️ Pas de route trouvée, veuillez selectionner un autre moyen de transport')
            except:
                st.subheader('Veuillez selectionner vos critères de vacances 🏝️')"""



if __name__ == "__main__":
    main()