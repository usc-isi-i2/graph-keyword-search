import json
import inflection
from SPARQLWrapper import SPARQLWrapper, JSON , XML
from colorAssignment import ColorAssignment
from wordSimilarity import WordSimilarity
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

	# This method is used to filter the predicates
	def filterPredicates(predicate,keywordList):

		# vocab dictionary contains the predicates that we do not want to consider
		vocabDictionary = ['rdf-schema#comment','22-rdf-syntax-ns#type','abstract','owl#sameAs','subject']

		predicateList = []

		# from the predicate URI, just consider the property and ignore the vocabulary
		# http://dbpedia.org/resource/Name  -----> consider 'Name'
		predicateValue = predicate.split('/')[-1]

		# ignore if the predicate property is in vocab dictionary
		if(predicateValue in vocabDictionary):
			return predicateList
		

		# Handles the camel case properties
		# camel cases will be returned seperated by _
		predicateValues = inflection.underscore(predicateValue).split('_')
		
		# camel case with _ to a string seperated by spaces
		actualPredicateValue = ''
		for value in predicateValues:
			actualPredicateValue = actualPredicateValue + ' ' + value

		actualPredicateValue = actualPredicateValue.strip()
		
		
		# iterate over each uncovered keyword and check if the predicate is semantically similar to the keyword
		for keyword in keywordList:
			# semantic similarity
			if(keyword.lower()==actualPredicateValue.lower()):
				score = 1.0
			else:
				score = WordSimilarity.isPredicateSimilar(keyword,actualPredicateValue)
				
			if(score!=-1):	
				predicateObject = Resource('<'+predicate+'>',predicateValue,0,keyword)
				
				# bi-gram scenario
				individualKeyword = keyword.split(' ')
				for key in individualKeyword:
					predicateObject.colors.append(ColorAssignment.colorDictionary[key])

				predicateObject.score = score
				predicateObject.isUri = True
				predicateList.append(predicateObject)

		return predicateList
	


	# This method is used to get the list of keywords that is not covered by the current element	
	def getUncoveredKeywords(colorList,biGramList):
		keywordList = []
		
		# Join the list to make it a single string
		pivotColors = ''.join(str(x) for x in colorList)			
		
		# Suppose we want to explore uncovered bi-grams, include them in the list
		if(len(biGramList)>0):
			keywordList.extend(biGramList)

		# make use of the color dictionary to identify uncovered keywords
		for keyword,color in ColorAssignment.colorDictionary.items():
			if(str(color) not in pivotColors):
				keywordList.append(keyword)

		return keywordList



	# Returns the triples for the pivot element
	def getAllTripletsForPivotElement(resource,biGramList):
		print(' Exploring ... ')
		tripletList = []
		# Get the URI of the element
		pivotElement = resource.uri									
		print(pivotElement)
		print('Current label : ' + resource.label)
		
		# Get a list of keywords that the current element does not cover
		keywordList = SparqlClient.getUncoveredKeywords(resource.colors,biGramList)
		print('Keywords yet to cover : ' + str(keywordList))

		# If the resource covers all keywords, stop exploring this node
		if(len(keywordList)==0):
			return tripletList


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

			# Considering only 'en' language
			if(result["o"]["type"]!= 'uri' ):
				if("xml:lang" in result['o'] and result["o"]["xml:lang"]!='en'):
					continue

			
			# Get the sematically similar predicates
			predicateList = SparqlClient.filterPredicates(result["p"]["value"],keywordList)
			
			for predicate in predicateList:
				
				isUri = False
				objectval = result["o"]["value"]
				
				# form the URI if object is of type URI
				if(result["o"]["type"]=='uri'):
					isUri = True
					objectval = '<'+objectval+'>'

				# remove duplicated keyword scenario
				set = []
				set.extend(resource.keyword.split(' '))
				for x in predicate.keyword.split(' '):
					if x not in set:
						set.append(x)
				
				set = ' '.join(str(x) for x in set)

				object = Resource(objectval,result["o"]["value"].split('/')[-1],0,set)

				# set the properties and form the fact node
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

