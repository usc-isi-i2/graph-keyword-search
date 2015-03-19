from SPARQLWrapper import SPARQLWrapper, JSON , XML
import json 
from colorAssignment import ColorAssignment
from wordSimilarity import WordSimilarity
import inflection
from collections import OrderedDict
from resourceGraph import Resource
from resourceGraph import FactNode

# This represents a DBPedia triplet object
class DBPediaTriplet:
	def __init__(self,subject,predicate,object):
		self.subject = subject
		self.object = object
		self.predicate = predicate



# This represents the sparql quering engine
class SparqlClient :

	predicateDictionary = {}
	

	# This method is used to filter the predicates
	def filterPredicates(predicate,keywordList):
		vocabDictionary = ['rdf-schema#comment','22-rdf-syntax-ns#type','abstract','owl#sameAs']
		predicateList = []

		predicateValue = predicate.split('/')[-1]

		if(predicateValue in vocabDictionary):
			return predicateList
		
		predicateValues = inflection.underscore(predicateValue).split('_')
		if(len(predicateValues)==1):
			wordSimilarityMeasure = 1
		else:
			wordSimilarityMeasure = 2

		val = ''
		for value in predicateValues:
			val = val + ' ' + value

		val = val.strip()
		
		#print(val)

		totalPredicates = 0
		for keyword in keywordList:
			score = WordSimilarity.isPredicateSimilar(keyword,val,wordSimilarityMeasure)
			if(score!=-1):
				#print(score)		
				predicateObject = Resource('<'+predicate+'>',predicateValue,0,keyword)
				predicateObject.colors.append(ColorAssignment.colorDictionary[keyword])
				predicateObject.score = score
				predicateObject.isUri = True
				predicateList.append(predicateObject)

		return predicateList
			
	# This method is used to get the list of keywords that is not covered by the current element	
	def getUncoveredKeywords(colorList):
		keywordList = []
		pivotColors = ''.join(str(x) for x in colorList)			# Join the list to make it a single string
		for keyword,color in ColorAssignment.colorDictionary.items():
			if(str(color) not in pivotColors):
				keywordList.append(keyword)
		return keywordList


	# Returns the triples for the pivot element
	def getAllTripletsForPivotElement(resource):

		tripletList = []
		print('Current label : ' + resource.label)
		# Get a list of keywords that the current element does not cover
		keywordList = SparqlClient.getUncoveredKeywords(resource.colors)
		print('Keywords yet to cover : ' + str(keywordList))
		if(len(keywordList)==0):
			return tripletList


		pivotElement = resource.uri									# Get the URI of the element
		print(pivotElement)
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
		except Exception as e:
			print(e)
			print(' DBPedia is down for maintanance')				# Exception
			return tripletList

		
		# Find predicates that are semantically similar to uncovered keywords 
		for result in results["results"]["bindings"]:
			if(result["o"]["type"]!= 'uri' ):
				if("xml:lang" in result['o'] and result["o"]["xml:lang"]!='en'):
					continue

			
			predicateList = SparqlClient.filterPredicates(result["p"]["value"],keywordList)
		
			for predicate in predicateList:
				
				isUri = False
				objectval = result["o"]["value"]
				if(result["o"]["type"]=='uri'):
					isUri = True
					objectval = '<'+objectval+'>'


				object = Resource(objectval,result["o"]["value"].split('/')[-1],0,'')
				if(isUri):
					object.isUri = True

				object.score = resource.score + predicate.score
				for color in resource.colors:
					if(color not in object.colors):
						object.colors.append(color)

				for color in predicate.colors:
					if(color not in object.colors):
						object.colors.append(color)

				factNodeObj = FactNode(resource,predicate,object)
				factNodeObj.score = object.score
				factNodeObj.set_colors()
				tripletList.append(factNodeObj)
			
		# Sort the list and return
		return tripletList

