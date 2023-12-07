from rdflib import Graph
import requests


def Complete_query(year):
    def query_wikidata(query):
        url = "https://query.wikidata.org/sparql"
        r = requests.get(url, params={"format": "json", "query": query})
        data = r.json()
        return data

    sparql_query = (
        """
    SELECT ?countryLabel ?hdiValue ?populationValue
    WHERE {
    ?country wdt:P31 wd:Q3624078;  # Instance of country
            wdt:P30 wd:Q46;        # Continent: Europe
            p:P1081 ?statement;    # Statement for HDI property
            p:P1082 ?statementPop.    # Statement for HDI property

    ?statement ps:P1081 ?hdiValue;
                pq:P585 ?dateHDI.      # Date qualifier for HDI property
    
    ?statementPop ps:P1082 ?populationValue;
                pq:P585 ?datePop. 
    
    FILTER ( YEAR(?dateHDI) = """
        + str(year)
        + """ && YEAR(?datePop) = YEAR(?dateHDI) ) 
    
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    ORDER BY ?countryLabel ?date
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

    return data_dict


print(Complete_query(2015))