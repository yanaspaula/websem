from SPARQLWrapper import SPARQLWrapper, JSON, POST, DIGEST, CSV
from flask import Flask, render_template
import json
import re 

app = Flask(__name__)




@app.route('/')
def get_data():
    sparql = SPARQLWrapper("http://localhost:3030/ds/")
    sparql.setQuery('''
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX ex: <http://example.com/#>
        PREFIX geo: <https://schema.org/GeoCoordinates/>
        PREFIX mv: <http://schema.mobivoc.org/#>

        SELECT ?latitude ?longitude ?id ?parking_name ?places ?type
        WHERE {
            GRAPH <http://www.semweb.com/project/parking_station>
                {
                    ?item geo:latitude ?latitude ;
                        geo:longitude ?longitude ;
                        mv:id ?id ;
                        mv:name ?parking_name ;
                        ex:hasParking 
                        [ 
                            mv:RealTimeCapacity ?places ;
                            mv:ParkingFacility ?type 
                        ]
                }
            }'''
                    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    parkings = results['results']['bindings']


    sparql.setQuery('''
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX ex: <http://example.com/#>
        PREFIX geo: <https://schema.org/GeoCoordinates/>
        PREFIX mv: <http://schema.mobivoc.org/#>

        SELECT ?latitude ?longitude ?id ?station_name ?plug ?bool ?status
        WHERE {
            GRAPH <http://www.semweb.com/project/electric_charger>
                {
                    ?item geo:latitude ?latitude ;
                        geo:longitude ?longitude ;
                        mv:id ?id ;
                        mv:name ?station_name ;
                        ex:hasPlug
                        [ 
                            mv:PlugType ?plug ;
                            mv:cableAvailable ?bool ;
                            ex:status ?status
                        ]
                }
            FILTER regex(?status, "Disponible")

            }'''
                    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    chargers = results['results']['bindings']
    with open("df_bornes.json") as f:
        jsonldChargers = json.load(f)
        # print(jsonldChargers)
        # jsonldChargers = json.loads(jsonldChargers)
    with open("df_parking.json") as f:
        jsonldParks = json.load(f)
        # jsonldParks =json.loads(jsonldChargers)

    return render_template('index.html', parks=parkings, chargers=chargers, jsonldChargers=jsonldChargers, jsonldParks=jsonldParks)


if __name__ == '__main__':
    app.run(debug=True)
