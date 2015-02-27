import urllib.request
import sys
import json

# Model class for pivot elements
class Pivot:
	def __init__(self,uri,label,support):
		# URI of the resource. DBPedia vocabulary
		self.uri = '<http://dbpedia.org/resource/'+uri+'>'
		# Label of the resource
		self.label = label
		# Importance/ represents the number of incoming links in DBPedia on to the resource
		self.support = support
		# Keyword represented by the resource
		self.keyword = ''


# Spotlight service for pivot entity recognition
class Spotlight:
	
	def __init__(self):
		sentence = ''

	# Parses the final resource values into a Pivot Object
	def getPivotObject(self,resource):

		# Get the URI, Label and Support
		if('@uri' in resource):
			uri = resource['@uri']
			label = ''
			support = 0

			if('@label' in resource):
				label = resource['@label']
				
			if('@support' in resource):
				try:
					support = int(resource['@support'])
				except ValueError:
					support = 0

			pivotElement = Pivot(uri,label,support)
			return pivotElement
		else:
			return None

	# Main logic of parsing implemented here
	def parseJson(self,jsonStr):
		
		#print(jsonStr)

		# Return list of pivot objects
		resourceList = []

		if('annotation' not in jsonStr):
			return resourceList

		if('surfaceForm' not in jsonStr['annotation']):
			return resourceList

		pivotTerms = jsonStr['annotation']['surfaceForm']
		
		#print(pivotTerms)

		# This happens only when the return type has one entity key word
		if(type(pivotTerms) is dict):
			#If there is no pivot entity
			if('resource' not in pivotTerms):
				return resourceList
			# If there is only one entity identified for the keyword
			if(type(pivotTerms['resource']) is dict):
				#If there is only one pivot identified for the query
				pivotElement = self.getPivotObject(pivotTerms['resource'])
				if(pivotElement is not None):
					pivotElement.keyword = pivotTerms['@name']
					resourceList.append(pivotElement)
			else:
				for resource in pivotTerms['resource']:
					pivotElement = self.getPivotObject(resource)
					if(pivotElement is not None):
						pivotElement.keyword = pivotTerms['@name']
						resourceList.append(pivotElement)

		# This happens when the return type has multiple entity keywords
		elif(type(pivotTerms) is list):
			
			for resources in pivotTerms:
				# This happens only when the return type has one entity key word
				if(type(resources) is dict):
					#If there is no pivot entity
					if('resource' not in resources):
						continue						
					# If there is only one entity identified for the keyword
					if(type(resources['resource']) is dict):
						#If there is only one pivot identified for the query
						pivotElement = self.getPivotObject(resources['resource'])
						if(pivotElement is not None):
							pivotElement.keyword = resources['@name']
							resourceList.append(pivotElement)
					else:
						for resource in resources['resource']:
							pivotElement = self.getPivotObject(resource)
							if(pivotElement is not None):
								pivotElement.keyword = resources['@name']
								resourceList.append(pivotElement)	
		#for res in resourceList:
			#print(res.uri+" "+res.label+" "+str(res.support))
		return resourceList

	# Queries DBPedia spotlight to get the values
	def requestSpotlight(self):
		#encode spaces
		sentence = self.sentence.replace(' ','%20')

		#restrict types to person,organistion and location
		urlTypes = 'types=DBpedia:Person,Schema:Person,DBpedia:Company,DBpedia:Organisation,Schema:Organization,DBpedia:AdministrativeRegion,DBpedia:PopulatedPlace,DBpedia:Place,Schema:Place'
		url = "http://spotlight.dbpedia.org/rest/candidates?types="+urlTypes+"&text="+sentence
		
		request = urllib.request.Request(url)
		request.add_header('Accept', 'application/json')
		response = urllib.request.urlopen(request)
		responseStr = str(response.read().decode('utf-8'))

		# fetch json from the response
		jsonStr = json.loads(responseStr)

		#Parse json
		return(self.parseJson(jsonStr))

	# Entry point of the class
	def getPivotElement(self,query):

		self.sentence = query
		#Make request
		return(self.requestSpotlight())
	
	
if __name__ == '__main__':
	spotlightObj = Spotlight()
	sentence = input(" Enter the keyword query : ")
	resourceList = spotlightObj.getPivotElement(sentence)

	if(len(resourceList)==0):
		print('no pivot entity found')
	else:
		for res in resourceList:
			print(res.uri+" "+res.label+" "+str(res.support)+" "+res.keyword)

