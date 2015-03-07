from SPARQLWrapper import SPARQLWrapper, JSON , XML
import json 
from colorAssignment import ColorAssignment
from wordSimilarity import WordSimilarity

# This represents a DBPedia triplet object
class DBPediaTriplet:
	def __init__(self,subject,predicate,object):
		self.subject = subject
		self.object = object
		self.predicate = predicate


class SparqlClient :

	predicateDictionary = {}

	def filterPredicates(predicate,keywordList):
		predicateValue = predicate.split('/')[-1]
		for keyword in keywordList:
			score = WordSimilarity.isPredicateSimilar(keyword,predicateValue)
			if(score):
				print(predicate+" "+keyword+" "+str(score))
				return True

		return False

		
	def getUncoveredKeywords(colorList):
		keywordList = []
		pivotColors = ''.join(str(x) for x in colorList)			# Join the list to make it a single string
		for keyword,color in ColorAssignment.colorDictionary.items():
			if(str(color) not in pivotColors):
				keywordList.append(keyword)
		return keywordList



	def getAllTripletsForPivotElement(resource):

		pivotElement = resource.uri									# Get the URI of the element
		tripletList = []
		sparql = SPARQLWrapper("http://dbpedia.org/sparql")			# Assigns an endpoint
		sparql.setReturnFormat(JSON)								# Sets the return format to be json
		# Queries the endpoint to retrive all the triplets that have pivot element as subject
		sparql.setQuery("""
		    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>			
		    SELECT ?p ?o
		    WHERE {  """ + pivotElement + """ ?p ?o
		      }
		      """)
			
		try:
			results = sparql.query().convert()
		except:
			print(' DBPedia is down for maintanance')				# Exception
			return tripletList

		# Get a list of keywords that the current element does not cover
		keywordList = SparqlClient.getUncoveredKeywords(resource.colors)

		if(len(keywordList)==0):
			return tripletList

		# Find predicates that are semantically similar to uncovered keywords 
		for result in results["results"]["bindings"]:
			SparqlClient.filterPredicates(result["p"]["value"],keywordList)
			#DBPediaTripletObj = DBPediaTriplet(pivotElement,result["p"]["value"],result["o"]["value"])
			
			#tripletList.append(DBPediaTripletObj)

		return tripletList

