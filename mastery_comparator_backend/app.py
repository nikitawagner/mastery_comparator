import json
import web
from rdflib import Graph
import requests

urls = (
    '/api', 'Index',
)

class Index:
    def OPTIONS(self):
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        web.header('Access-Control-Allow-Headers', 'Content-Type')
        return
    
    def POST(self):
        web.header('Access-Control-Allow-Origin', '*')  
        try:
            year = json.loads(web.data().decode("utf-8"))['year']
            year = int(year)
            # check if year is an integer between 1999 and 2021
            if year < 1999 or year > 2021:
                web.ctx.status = '400 Bad Request'
                return json.dumps({
                    "status": "error",
                    "message": "year must be an integer between 1999 and 2021"
                })
            try:
                result = make_sparql_request(year)
                return json.dumps({
                    "status": "success",
                    "data": result
                })
            except Exception as e:
                web.ctx.status = '500 Internal Server Error'
                return json.dumps({
                    "status": "error",
                    "message": str(e)
                })
        except Exception as e:
            web.ctx.status = '400 Bad Request'
            return json.dumps({
                "status": "error",
                "message": str(e)
            })

    if __name__ == "__main__":
        app = web.application(urls, globals())
        app.run()
    
def make_sparql_request(year):
    def query_wikidata(query):
        url = "https://query.wikidata.org/sparql"
        r = requests.get(url, params={"format": "json", "query": query})
        data = r.json()
        return data

    sparql_query = (
        """
    SELECT ?countryLabel ?hdiValue ?populationValue
    WHERE {
    ?country wdt:P31 wd:Q3624078;  
            wdt:P30 wd:Q46;       
            p:P1081 ?statement;   
            wdt:P1082 ?populationValue.

    ?statement ps:P1081 ?hdiValue;
                pq:P585 ?dateHDI.

    FILTER (YEAR(?dateHDI) = """
        + str(year)
        + """) 

    SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    ORDER BY ?countryLabel
    """
    )

    wikidata_results = query_wikidata(sparql_query)

    # ---

    g = Graph()
    g.parse("data.ttl", format="turtle")

    sparql_query = (
        """
    PREFIX iut: <http://www.iut-orsay.fr/Wagner/>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?pays ?accident ?annee
    WHERE {
        ?individu iut:pays ?pays .
        ?individu iut:annee ?annee .
        ?individu iut:accident ?accident .
        
        FILTER (?annee = """
        + str(year)
        + """)
    }
    order by desc(?accident)
    """
    )

    data_results = g.query(sparql_query)

    # ---

    data_dict = {}
    for row in wikidata_results["results"]["bindings"]:
        for result in data_results:
            if str(result[0]) == row["countryLabel"]["value"]:
                data_dict[row["countryLabel"]["value"]] = {
                    "country": row["countryLabel"]["value"],
                    "hdi": float(row["hdiValue"]["value"]),
                    "accident": int(float(str(result[1]))),
                    "annee": int(str(result[2])),
                    "population": int(row["populationValue"]["value"]),
                }

    data_dict = sorted(
        data_dict.values(),
        key=lambda x: x["accident"] * x["hdi"] / x["population"],
        reverse=True,
    )
    print(data_dict)
    new_data = {entry['country'].lower(): {
    'hdi': entry['hdi'],
    'accident': entry['accident'],
    'population': entry['population'],
    'year': entry['annee'],
    'accidentRatePer100k': (entry['accident'] / entry['population']) * 100000,
    'adjustedAccidentRate': ((entry['accident'] / entry['population']) * 100000) / entry['hdi']
    } for entry in data_dict}

    return new_data
