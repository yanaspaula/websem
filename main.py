import urllib.request
import json
from rdflib  import URIRef, BNode, Literal, Graph
from rdflib import Namespace
from rdflib.namespace import RDF, FOAF, RDFS, XSD

# Namespaces
mv = Namespace('http://schema.mobivoc.org/#')
geo = Namespace('https://schema.org/GeoCoordinates/')


# Importation des données
with urllib.request.urlopen("https://www.data.gouv.fr/fr/datasets/r/556d828f-2643-4bd9-97ed-38b6f4b369e5") as url:
    df_bornes = json.loads(url.read().decode())

# --------- Graphe Chargeurs Electriques --------- #
graph = Graph()

# Création des namespaces dans le graphe
graph.namespace_manager.bind('mv', mv, override = False)
graph.namespace_manager.bind('geo', geo, override = False)

for row in df_bornes : 
    station_id = Literal(row['fields']['plugs_chargepointid'].replace('*', ''))
    name_station = Literal(row['fields']['static_name'], datatype=XSD.string)
    plug_model = Literal(row['fields']['plugs_outletmodel'], datatype=XSD.string)
    status = Literal(row['fields']['plugs_status'], datatype=XSD.string)
    latitude = Literal(row['fields']['geolocation_coordinates'][0],  datatype = XSD.decimal)
    longitude = Literal(row['fields']['geolocation_coordinates'][1],  datatype = XSD.decimal)

    item = URIRef('http://www.semweb.com/project/electric_charger#' + station_id)

    # Création des triplets (statics)
    graph.add((item, mv.id, station_id))
    # graph.add((item, mv.powerInKW, power))
    graph.add((item, mv.PlugType, plug_model)) # Does not use members of ontology
    graph.add((item, geo.latitude, latitude))
    graph.add((item, geo.longitude, longitude))

graph.serialize(destination = "df_bornes.ttl", format = "turtle")
