# Pip install sparql
from SPARQLWrapper import SPARQLWrapper, JSON


# Sparql Query to get labels using Qids
def get_item_label(qid):
    try:
        # Specifying the Wikidata SPARQL endpoint
        sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

        # Query to access the label for the wikidata item
        sparql.setQuery(
            'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> SELECT ?label WHERE {wd:' + qid + ' rdfs:label ?label . SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } } LIMIT 1')

        # Converting result to JSON format
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()

        # result is in the form of "bindings" which are a list of dictionaries
        # Accessing the value of the label
        itemLabel = result["results"]["bindings"][0]["label"]["value"]

        return itemLabel
    except Exception as ex:
        print(ex)
        return ('')