import streamlit as st
import pandas as pd
import folium
import subprocess
import sys
from streamlit_folium import st_folium
from pyroutelib3 import Router
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from sklearn.neighbors import NearestNeighbors
from sklearn.neighbors import KNeighborsRegressor
from geopy.geocoders import Nominatim

APP_TITLE = "Itinéraire de vacances 🏁"
APP_SUBTITLE = 'Itinéraire de vacances 🏁'

#df = pd.read_csv("./POI.csv")

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

@st.cache_resource
def print_map(moyenLocomtion: str, coordonneesHotels):
    router = Router(moyenLocomtion)
    listePoints = []
    listeCoord = []
    
    for hotel in coordonneesHotels:
        listePoints.append(router.findNode(*hotel))
        listeCoord.append(hotel)
    optmizePlan = itineraire_villes(moyenLocomtion, *listeCoord)
    m = folium.Map(location=(router.nodeLatLon(listePoints[0])),
                   tiles="OpenStreetMap",
                   zoom_start=16)
    for index in range(len(listePoints)):
        start = listePoints[optmizePlan[index]]
        end = listePoints[optmizePlan[index + 1]]
        status, route = router.doRoute(start, end)
        
        if status != 'success':
            raise NoRoute

        route_latLon = list(map(router.nodeLatLon, route))

            
        folium.PolyLine(route_latLon, weight=5, opacity=.4).add_to(m)
        folium.Marker(
        location = router.nodeLatLon(start),
        popup = index, opacity=.8).add_to(m)
    
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
    
    total_coord = [(latVille, lonVille)] + listeCoordoneesPoi
    
    m = print_map(moyenLocomtion=modeTransport, coordonneesHotels=total_coord)
    st_map = st_folium(m, width=700, height=450)
    return st_map


def find_coord(ville: str):
    geolocator = Nominatim(user_agent="my_geocoder")
    location = geolocator.geocode(ville)
    return location.latitude, location.longitude

# knnHotel = KNeighborsRegressor(n_neighbors=1)
# knnHotel.fit(df[df['type2'] == 'Accommodation'][['latitude', 'longitude']],
#              df[df['type2'] == 'Accommodation'][['latitude', 'longitude']])


def main(df):
    #os.system("streamlit run /home/ubuntu/ItineraireDeVoyage/app/db_postgre/map.py")  
    subprocess.run([f"{sys.executable}", "map.py"])
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)

    # Choix des constantes
    

    liste_ville = list(df.Ville.value_counts().index)
    ville = st.sidebar.text_input('Ville')
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

    try:
        appOneDay(types, ville, trad_transport[mode_transport], max_poi, df)
    except NoRoute:
        st.caption('⚠️ Pas de route trouvée, veuillez selectionner un autre moyen de transport')
    except:
        st.subheader('Veuillez selectionner vos critères de vacances 🏝️')



if __name__ == "__main__":
    main()