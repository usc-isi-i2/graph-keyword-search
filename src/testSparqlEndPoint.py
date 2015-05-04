import urllib.request
import sys
import json
import math
from urllib.parse import quote
from SPARQLWrapper import SPARQLWrapper, JSON , XML

sparql = SPARQLWrapper("http://dbpedia.org/sparql")			# Assigns an endpoint
sparql.setReturnFormat(JSON)								# Sets the return format to be json
# Queries the endpoint to retrive all the triplets that have pivot element as subject
pivotElement = '<http://dbpedia.org/resource/Angela_Merkel>'


sparql.setQuery("""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>			
    SELECT ?p ?label
    WHERE {  """ + pivotElement + """ ?p ?label
      }
      """)
'''
sparql.setQuery("""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?label
    WHERE { 
      <http://dbpedia.org/resource/Asturias> rdfs:label ?label .
    }
""")
'''

try:
	results = sparql.query().convert()
except Exception as e:
  print(e)
  print(' DBPedia is down for maintanance')
  exit(3)

# Find predicates that are semantically similar to uncovered keywords 
for result in results["results"]["bindings"]:

	# Considering only 'en' language
	print(result["label"]["value"])


print('done')
