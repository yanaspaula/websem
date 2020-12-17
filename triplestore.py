import requests
from urllib.request import urlopen
from requests_toolbelt.multipart.encoder import MultipartEncoder 
import json
from rdflib import URIRef, BNode, Literal, Graph, Namespace
from rdflib.namespace import RDF, FOAF, RDFS, XSD

# Namespaces
mv = Namespace('http://schema.mobivoc.org/#')
geo = Namespace('https://schema.org/GeoCoordinates/')
ex = Namespace('http://example.com/#')


# Importation des données
#with urllib.request.urlopen("https://www.data.gouv.fr/fr/datasets/r/556d828f-2643-4bd9-97ed-38b6f4b369e5") as url:
with urlopen("https://www.data.gouv.fr/fr/datasets/r/556d828f-2643-4bd9-97ed-38b6f4b369e5") as url:
    df_bornes = json.loads(url.read().decode())
#with urllib.request.urlopen("https://www.data.gouv.fr/fr/datasets/r/0fb3fe0e-2a69-45ac-aca7-6923d18698bc") as url:
with urlopen("https://www.data.gouv.fr/fr/datasets/r/0fb3fe0e-2a69-45ac-aca7-6923d18698bc") as url:
    df_parking = json.loads(url.read().decode())

# Supprimer les entrées sans géolocalisation
def filterData(x):
    if "geo" in x["fields"].keys():
        return(True)
    return(False)

df_parking = list(filter(filterData, df_parking))

# Création des graphes
graphE = Graph(identifier="ElectricChargers")
graphP = Graph(identifier="Parkings")

# Création des namespaces dans le graph
graphE.namespace_manager.bind('mv', mv, override=False)
graphE.namespace_manager.bind('geo', geo, override=False)
graphE.namespace_manager.bind('ex', ex, override=False)
graphP.namespace_manager.bind('mv', mv, override=False)
graphP.namespace_manager.bind('geo', geo, override=False)
graphP.namespace_manager.bind('ex', ex, override=False)

# RDF Chargeurs
for row in df_bornes:
    row = row['fields']
    station_id = Literal(row['plugs_chargepointid'].replace('*', ''))
    name_station = Literal(row['static_name'], datatype=XSD.string)
    latitude = Literal(
        row['geolocation_coordinates'][0],  datatype=XSD.decimal)
    longitude = Literal(
        row['geolocation_coordinates'][1],  datatype=XSD.decimal)
    
    status = Literal(row['plugs_status'], datatype=XSD.string)
    plug_model = Literal(
        row['plugs_outletmodel'], datatype=XSD.string)
    blank_node = BNode()

    item = URIRef(
        'http://www.semweb.com/project/electric_charger#' + station_id)

    # Création des triplets (statics)
    graphE.add((item, mv.id, station_id))
    graphE.add((item, mv.name, name_station))
    graphE.add((item, geo.latitude, latitude))
    graphE.add((item, geo.longitude, longitude))

    # Création des triplets (dynamiques)
    graphE.add((item, ex.hasPlug, blank_node))
    graphE.add((blank_node, mv.PlugType, plug_model))
    graphE.add((blank_node, ex.status, status))
    if row['plugs_status'] == 'Disponible':
        graphE.add((blank_node, mv.cableAvailable, Literal(True, datatype=XSD.boolean))) # DOIT ÊTRE BOOLEAN
    else:
        graphE.add((blank_node, mv.cableAvailable, Literal(False, datatype=XSD.boolean))) # DOIT ÊTRE BOOLEAN

graphE.serialize(destination="df_bornes.ttl", format="turtle")

# RDF stationnements
for row in df_parking:
    row = row['fields']
    station_id = Literal(row['facilityid'])
    name_station = Literal(row['nom_parking'], datatype=XSD.string)
    latitude = Literal(row['geo'][0],  datatype=XSD.decimal)
    longitude = Literal(row['geo'][1],  datatype=XSD.decimal)

    freePlaces = Literal(row['counterfreeplaces'], datatype=XSD.integer)
    typePlaces = Literal(row['countertype'], datatype=XSD.string)
    blank_node = BNode()

    item = URIRef('http://www.semweb.com/project/parking_station#' + station_id)

    # Création des triplets (statics)
    graphP.add((item, mv.id, station_id))
    graphP.add((item, mv.name, name_station))
    graphP.add((item, geo.latitude, latitude))
    graphP.add((item, geo.longitude, longitude))
    
    # Création des triplets (dynamique)
    graphP.add((item, ex.hasParking, blank_node))
    graphP.add((blank_node, mv.RealTimeCapacity, freePlaces))
    graphP.add((blank_node, mv.ParkingFacility, typePlaces))
    # TODO: associer real time capacity with its corresponding time
    
graphP.serialize(destination="df_parking.ttl", format="turtle")

# Automatisation de l'upload sur Fuseki 
chargeurs_data = MultipartEncoder(fields={'file': ('df_bornes.ttl', open('df_bornes.ttl', 'rb'), 'text/turtle')}) 
parking_data = MultipartEncoder(fields={'file': ('df_parking.ttl', open('df_parking.ttl', 'rb'), 'text/turtle')}) 
put_bornes = requests.put('http://localhost:3030/ds/data?graph=http://www.semweb.com/project/electric_charger#', data=chargeurs_data, auth=('admin','mypassword'),headers={'Content-Type': chargeurs_data.content_type})
put_parking = requests.put('http://localhost:3030/ds/data?graph=http://www.semweb.com/project/parking_station#', data=parking_data, auth=('admin','mypassword'),headers={'Content-Type': parking_data.content_type})
