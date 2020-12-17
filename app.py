from SPARQLWrapper import SPARQLWrapper, JSON, POST, DIGEST, CSV
from flask import Flask, render_template
import json


app = Flask(__name__)




@app.route('/')
def get_data():
    sparql = SPARQLWrapper("http://localhost:3030/ds/")
    sparql.setQuery('''
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX ex: <http://example.com/#>
        PREFIX geo: <https://schema.org/GeoCoordinates/>
        PREFIX mv: <http://schema.mobivoc.org/#>

        SELECT ?latitude ?longitude ?places ?type
        WHERE {
            GRAPH <http://www.semweb.com/project/parking_station>
                {
                    ?item geo:latitude ?latitude ;
                        geo:longitude ?longitude;
                        ex:hasParking 
                        [ 
                            mv:RealTimeCapacity ?places;
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

        SELECT ?latitude ?longitude ?plug ?bool ?status
        WHERE {
            GRAPH <http://www.semweb.com/project/electric_charger>
                {
                    ?item geo:latitude ?latitude ;
                        geo:longitude ?longitude ;
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

    return render_template('index.html', parks=parkings, chargers=chargers)


if __name__ == '__main__':
    app.run(debug=True)
