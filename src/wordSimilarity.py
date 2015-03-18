import urllib.request
import sys
import json
from urllib.parse import quote

class WordSimilarity:
	def getEasyESAScore(word1,word2):
		url = "http://vmdeb20.deri.ie:8890/esaservice?task=esa&term1="+quote(word1)+'&term2='+quote(word2)
		request = urllib.request.Request(url)
		response = urllib.request.urlopen(request)
		score = str(response.read().decode('utf-8')).replace('\"','')
		return float(score)

	def getWs4jScore(word1,word2):
		url = "http://ws4jdemo.appspot.com/ws4j?measure=wup&args="+word1+"%3A%3A"+word2
		request = urllib.request.Request(url)
		request.add_header('Accept', 'application/json')
		response = urllib.request.urlopen(request)
		responseStr = response.read().decode('utf-8')
		# fetch json from the response
		jsonStr = json.loads(responseStr)	
		return float(jsonStr['result'][0]['score'])
	
	def isPredicateSimilar(word1,word2,option):
		score = -1
		if(option!=1):
			score = WordSimilarity.getEasyESAScore(word1,word2)
			if(score!=0 or score!=-1):
				return score
			else:
				return -1
		else:
			score = WordSimilarity.getEasyESAScore(word1,word2)
			#score = WordSimilarity.getWs4jScore(word1,word2)
			#if(score>0.8):
			if(score!=0 or score!=-1):
				return score
			else:
				return -1
		
	
