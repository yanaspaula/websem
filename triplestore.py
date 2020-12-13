
# Hanane OUBLOUHOU
# Yana SOARES DE PAULA
# --------------------------------------------------------------
# Initialization
import numpy as np
import pandas as pd
from rdflib  import URIRef, BNode, Literal, Graph, Namespace
from rdflib.namespace import RDF, FOAF, RDFS, XSD
import re
import jaydebeapi

# Importation des données
df_bornes = pd.read_csv("https://www.data.gouv.fr/en/datasets/r/50625621-18bd-43cb-8fde-6b8c24bdabb3", sep=';')
df_stat = pd.read_csv("https://www.data.gouv.fr/en/datasets/r/e32f7675-913b-4e01-b8c8-0a29733e4407", sep=";")

# Pré-traitement des données
df_bornes = df_bornes.dropna(subset=['Xlongitude', 'Ylatitude']) # Suppression des données sans lat/long
df_bornes.index = np.arange(len(df_bornes))	# Indexes commencent par 0
df_stat = df_stat.dropna(subset=['Xlong', 'Ylat'])	# Suppression des données sans lat/long
df_stat.index = np.arange(len(df_stat)) # Indexes commencent par 0

# Namespaces
mv = Namespace('http://schema.mobivoc.org/#')
geo = Namespace('https://schema.org/GeoCoordinates/')

# --------- Graphe Chargeurs Electriques --------- #
graph = Graph()

# Création des namespaces dans le graphe
graph.namespace_manager.bind('mv', mv, override = False)
graph.namespace_manager.bind('geo', geo, override = False)

# Parsing des données df_bornes
for row in range(len(df_bornes)):
	# TODO: définir différences entre villes - regex (!)
	item = URIRef('http://www.semweb.com/project/electric_charger#' + str(df_bornes['id_station'][row]).replace('*', '').replace(' ', ''))

	# Objects
	station_id = Literal(str(df_bornes['id_station'][row]).replace('*', '').replace(' ', ''), datatype = XSD.string)
	power = Literal(df_bornes['puiss_max'][row], datatype = XSD.double)
	plug = Literal(df_bornes['type_prise'][row])
	latitude = Literal(df_bornes['Ylatitude'][row].replace('*', ''), datatype = XSD.decimal)
	longitude = Literal(df_bornes['Xlongitude'][row].replace('*', ''), datatype = XSD.decimal)

	# Création des triplets (statics)
	graph.add((item, mv.id, station_id))
	graph.add((item, mv.powerInKW, power))
	graph.add((item, mv.PlugType, plug)) # Does not use members of ontology
	graph.add((item, geo.latitude, latitude))
	graph.add((item, geo.longitude, longitude))	

graph.serialize(destination = "df_bornes.ttl", format = "turtle")

# --------- Graphe Stationements --------- #
graph = Graph()

# Création des namespaces dans le graphe
graph.namespace_manager.bind('mv', mv, override = False)
graph.namespace_manager.bind('geo', geo, override = False)

# Parsing des données df_stat
for row in range(len(df_stat)):
	# TODO: définir différences entre villes - regex (!)
	item = URIRef('http://www.semweb.com/project/parking_lot#' + str(df_stat['id'][row]))

	# Objects
	parking_id = Literal(str(df_stat['id'][row]), datatype = XSD.string)
	nombre_places = Literal(df_stat['nb_places'][row], datatype = XSD.integer)
	adresse = Literal(df_stat['adresse'][row], datatype = XSD.string)
	latitude = Literal(df_bornes['Ylatitude'][row].replace('*', ''), datatype = XSD.decimal)
	longitude = Literal(df_bornes['Xlongitude'][row].replace('*', ''), datatype = XSD.decimal)

	# Création des triplets (statics)
	graph.add((item, mv.id, parking_id))
	graph.add((item, mv.totalCapacity, nombre_places))
	graph.add((item, geo.address, adresse))	
	graph.add((item, geo.latitude, latitude))
	graph.add((item, geo.longitude, longitude))
	
graph.serialize(destination = "df_stat.ttl", format = "turtle")

# --------- Insertion Jena Fuseki --------- #


# Sources
# https://www.data.gouv.fr/en/datasets/base-nationale-des-lieux-de-stationnement/?fbclid=IwAR1iRO4HrBGyGv4kX_HEl6G9v5MVEcNcU2z9sCFoFLqg0hYYeBYvKgH_Pvw
# https://www.data.gouv.fr/en/datasets/fichier-consolide-des-bornes-de-recharge-pour-vehicules-electriques/?fbclid=IwAR2lNLUMUW1H7tCHDvczhSiq-lBMSWmTsVepblc0DfHbXJVvIc5gkub6yRs#_

# Namespace #
# GeoNames
# https://www.geonames.org/ontology/ontology_v3.2.rdf
# mobVoc
# http://schema.mobivoc.org/