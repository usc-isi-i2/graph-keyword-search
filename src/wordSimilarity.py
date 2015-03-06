import urllib.request
import sys
import json

class WordSimilarity:

	def getSimilarityValue(word1,word2):

		url = "http://vmdeb20.deri.ie:8890/esaservice?task=esa&term1="+word1+'&term2='+word2
		request = urllib.request.Request(url)
		response = urllib.request.urlopen(request)

		print (response.read().decode('utf-8'))

	

	# Use ws4j for predicate similarity
	# Using threshold as 0.8
	# If you don't find the word in ws4j, use EasyESA
	def isPredicateSimilar(word1,word2):
		url = "http://ws4jdemo.appspot.com/ws4j?measure=wup&args="+word1+"%3A%3A"+word2
		request = urllib.request.Request(url)
		request.add_header('Accept', 'application/json')
		response = urllib.request.urlopen(request)
		responseStr = response.read().decode('utf-8')
		# fetch json from the response
		jsonStr = json.loads(responseStr)

		score = float(jsonStr['result'][0]['score'])
		if(score>0.8):
			return True
		elif(score==-1):
			return False
		else:
			return False


