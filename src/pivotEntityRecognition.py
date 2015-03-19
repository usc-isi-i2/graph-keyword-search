import urllib.request
import sys
import json
from resourceGraph import Resource
from colorAssignment import ColorAssignment

# Spotlight service for pivot entity recognition
class PivotEntityRecognition:
	
	def __init__(self):
		sentence = ''

	# This method updates the colours covered by a resource
	def updateColors(self,resourceList):
		for res in resourceList:
			tokens = res.keyword.split(' ')
			for token in tokens:
				if(token in ColorAssignment.colorDictionary):
					res.colors.append(int(ColorAssignment.colorDictionary[token]))

		return resourceList


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

			pivotElement = Resource('<http://dbpedia.org/resource/'+uri+'>',label,support,'')
			pivotElement.isUri = True
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

		# Sort the resource list on the number of incoming links
		resourceList.sort(key=lambda x: x.support, reverse=True)
		# Update the colors represented by the resources
		resourceList = self.updateColors(resourceList)

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
	spotlightObj = PivotEntityRecognition()
	sentence = input(" Enter the keyword query : ")
	resourceList = spotlightObj.getPivotElement(sentence)

	if(len(resourceList)==0):
		print('no pivot entity found')
	else:
		for res in resourceList:
			print(res.uri+" "+res.label+" "+str(res.support)+" "+res.keyword)

