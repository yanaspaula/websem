import urllib.request
import json
from rdflib import URIRef, BNode, Literal, Graph
from rdflib import Namespace
from rdflib.namespace import RDF, FOAF, RDFS, XSD

# Namespaces
mv = Namespace('http://schema.mobivoc.org/#')
geo = Namespace('https://schema.org/GeoCoordinates/')
ex = Namespace('http://example.com/#')


# Importation des données
with urllib.request.urlopen("https://www.data.gouv.fr/fr/datasets/r/556d828f-2643-4bd9-97ed-38b6f4b369e5") as url:
    df_bornes = json.loads(url.read().decode())
with urllib.request.urlopen("https://www.data.gouv.fr/fr/datasets/r/0fb3fe0e-2a69-45ac-aca7-6923d18698bc") as url:
    df_parking = json.loads(url.read().decode())


def filterData(x):
    if "geo" in x["fields"].keys():
        return(True)
    return(False)


df_parking = list(filter(filterData, df_parking))
for row in df_parking:
    print(row)
# --------- Graphe Chargeurs Electriques --------- #
graphE = Graph(identifier="ElectricChargers")
graphP = Graph(identifier="Parkings")

# Création des namespaces dans le graph
graphE.namespace_manager.bind('mv', mv, override=False)
graphE.namespace_manager.bind('geo', geo, override=False)
graphE.namespace_manager.bind('ex', ex, override=False)
graphP.namespace_manager.bind('mv', mv, override=False)
graphP.namespace_manager.bind('geo', geo, override=False)
graphP.namespace_manager.bind('ex', ex, override=False)

for row in df_bornes:
    station_id = Literal(row['fields']['plugs_chargepointid'].replace('*', ''))
    name_station = Literal(row['fields']['static_name'], datatype=XSD.string)
    plug_model = Literal(
        row['fields']['plugs_outletmodel'], datatype=XSD.string)
    status = Literal(row['fields']['plugs_status'], datatype=XSD.string)
    latitude = Literal(
        row['fields']['geolocation_coordinates'][0],  datatype=XSD.decimal)
    longitude = Literal(
        row['fields']['geolocation_coordinates'][1],  datatype=XSD.decimal)

    item = URIRef(
        'http://www.semweb.com/project/electric_charger#' + station_id)

    # Création des triplets (statics)
    graphE.add((item, mv.id, station_id))
    # graphE.add((item, mv.powerInKW, power))
    graphE.add((item, mv.PlugType, plug_model))
    graphE.add((item, geo.latitude, latitude))
    graphE.add((item, geo.longitude, longitude))
    graphE.add((item, ex.IsAvailable, status))

for row in df_parking:
    row = row['fields']
    station_id = Literal(row['facilityid'])
    name_station = Literal(row['nom_parking'], datatype=XSD.string)
    park_type = Literal(row['type_de_parc'], datatype=XSD.string)
    freePlaces = Literal(row['counterfreeplaces'], datatype=XSD.integer)
    latitude = Literal(row['geo'][0],  datatype=XSD.decimal)
    longitude = Literal(row['geo'][1],  datatype=XSD.decimal)

    item = URIRef('http://www.semweb.com/project/ParkingStation#' + station_id)

    # Création des triplets (statics)
    graphP.add((item, mv.id, station_id))
    graphP.add((item, geo.latitude, latitude))
    graphP.add((item, geo.longitude, longitude))
    graphP.add((item, ex.hasFreePlaces, freePlaces))
    graphP.add((item, ex.hastype, park_type))

graphP.serialize(destination="df_parking.ttl", format="turtle")


""" 
    TO DO:
    1- Finaliser l'ontologie 
    2- Automatiser l'upload au TripleStore (Fuseki)
    3- Ecrire les requetes SPARQL 
    4- Créer les vues et gérér leur rendering (Django)

"""