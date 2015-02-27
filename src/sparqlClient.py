from SPARQLWrapper import SPARQLWrapper, JSON , XML
import json 

# This represents a DBPedia triplet object
class DBPediaTriplet:
	def __init__(self,subject,predicate,object):
		self.subject = subject
		self.object = object
		self.predicate = predicate


class SparqlClient :

	def getAllTripletsForPivotElement(pivotElement):

		tripletList = []

		sparql = SPARQLWrapper("http://dbpedia.org/sparql")			# Assigns an endpoint
		
		# Queries the endpoint to retrive all the triplets that have pivot element as subject
		sparql.setQuery("""
		    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>			
		    SELECT ?p ?o
		    WHERE {  """ + pivotElement + """ ?p ?o
		      }
		      """)
			
		sparql.setReturnFormat(JSON)

		try:
			results = sparql.query().convert()
		except:
			# HTTP Error 502
			print(' DBPedia is down for maintanance')
			return tripletList

		for result in results["results"]["bindings"]:
			DBPediaTripletObj = DBPediaTriplet(pivotElement,result["p"]["value"],result["o"]["value"])
			tripletList.append(DBPediaTripletObj)

		return tripletList

