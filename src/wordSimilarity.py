import urllib.request
import sys
import json
from urllib.parse import quote
		

class WordSimilarity:

	# 1 - EasyESA client
	# a score of 1 and -1 results in a perfect match
	# treshold values to consider  0.07, 0.052 and 0.04
	def getEasyESAScore(word1,word2):
		url = "http://vmdeb20.deri.ie:8890/esaservice?task=esa&term1="+quote(word1)+'&term2='+quote(word2)
		request = urllib.request.Request(url)
		response = urllib.request.urlopen(request)
		score = str(response.read().decode('utf-8')).replace('\"','')
		return float(score)

	# 2 - ws4j client
	def getWs4jScore(word1,word2):
		url = "http://ws4jdemo.appspot.com/ws4j?measure=wup&args="+quote(word1)+"%3A%3A"+quote(word2)
		#print(url)
		request = urllib.request.Request(url)
		request.add_header('Accept', 'application/json')
		response = urllib.request.urlopen(request)
		responseStr = response.read().decode('utf-8')
		# fetch json from the response
		jsonStr = json.loads(responseStr)
		score = float(jsonStr['result'][0]['score'])
		return score
	
	
	# As of now using only EasyESA.
	# call the method 2 ws4j client if needed
	# a score of 1 and -1 results in a perfect match
	# treshold values to consider  0.07, 0.052 and 0.04
	def isPredicateSimilar(word1,word2):
		score = WordSimilarity.getEasyESAScore(word1,word2)
		if(score>0.07):
			return score
		else:
			return -1
	
	'''	
	def isPredicateSimilar(word1,word2,option):
		score = -1
		if(option!=1 or option!=2):
			#score = WordSimilarity.getEasyESAScore(word1,word2)
			score = 0
			if((score!=0 or score!=-1) and score>0.1):
				return score
			else:
				score = WordSimilarity.getWs4jScore(word1,word2)
				if(score>0.8):
					return score
				else:
					return -1
	'''	
