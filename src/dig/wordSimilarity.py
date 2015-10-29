import urllib.request
import sys
import json
import math
from urllib.parse import quote
from threading import Thread

class WordSimilarity:

	scoreDictionary = {}
	scoreDictionary['esa'] = 0
	scoreDictionary['swoogle'] = 0

	# 1 - EasyESA client
	# a score of 1 and -1 results in a perfect match
	# treshold values to consider  0.07, 0.052 and 0.04
	def getEasyESAScore(word1,word2):

		WordSimilarity.scoreDictionary['esa'] = 0
		url = "http://vmdeb20.deri.ie:8890/esaservice?task=esa&term1="+quote(word1)+'&term2='+quote(word2)
		try:
			request = urllib.request.Request(url)
			response = urllib.request.urlopen(request)
			score = str(response.read().decode('utf-8')).replace('\"','')
			if float(score)> 0:
				print("ESA %s %s => %s" % (word1, word2, score))
			WordSimilarity.scoreDictionary['esa'] = float(score)
		except Exception as e:
			WordSimilarity.scoreDictionary['esa'] = 0

	# 2 - ws4j client
	def getWs4jScore(word1,word2):
		url = "http://ws4jdemo.appspot.com/ws4j?measure=wup&args="+quote(word1)+"%3A%3A"+quote(word2)
		request = urllib.request.Request(url)
		request.add_header('Accept', 'application/json')
		response = urllib.request.urlopen(request)
		responseStr = response.read().decode('utf-8')
		# fetch json from the response
		jsonStr = json.loads(responseStr)
		score = float(jsonStr['result'][0]['score'])
		return score
	
	# 3 - UMBC Semantic Similarity service
	#
	#  Documentation availabel at http://swoogle.umbc.edu/SimService/api.html
	def getSwoogleScore(word1,word2):
		WordSimilarity.scoreDictionary['swoogle'] = 0	
		url = "http://swoogle.umbc.edu/StsService/GetStsSim?operation=api&phrase1="+quote(word1)+'&phrase2='+quote(word2)
		try:
			request = urllib.request.Request(url)
			response = urllib.request.urlopen(request)
			score = str(response.read().decode('utf-8')).replace('\"','')
			score = float(score)
			if score > 0:
				print("Swoogle %s / %s => %s" % (word1, word2, score))
			WordSimilarity.scoreDictionary['swoogle'] = score
		except Exception as e:
			WordSimilarity.scoreDictionary['swoogle'] = 0


	# As of now using only EasyESA.
	# call the method 2 ws4j client if needed
	# a score of 1 and -1 results in a perfect match
	# treshold values to consider  0.07, 0.052 and 0.04
	def isPredicateSimilar(word1,word2):
		#score = math.fabs(WordSimilarity.getEasyESAScore(word1,word2))
		        
	    esaThread = Thread(target=WordSimilarity.getEasyESAScore, args=(word1,word2,))
	    swoogleThread = Thread(target=WordSimilarity.getSwoogleScore, args=(word1,word2,))

	    esaThread.start()
	    swoogleThread.start()
	    esaThread.join()
	    swoogleThread.join()

	    ESAscore = WordSimilarity.scoreDictionary['esa'] 
	    #WordSimilarity.getEasyESAScore(word1,word2)
	    ESAScaledScore = 0
	    if(ESAscore>0 and ESAscore<=0.04):
	    	ESAScaledScore = 1
	    elif(ESAscore>0.04 and ESAscore<=0.06):
	    	ESAScaledScore = 2
	    elif(ESAscore>0.07):
	    	ESAScaledScore = 3
	    else:
	    	ESAScaledScore = 0

	    SwoogleScore = WordSimilarity.scoreDictionary['swoogle'] 
	    # WordSimilarity.getSwoogleScore(word1,word2)
	    SwoogleScaledScore = 0
	    if(SwoogleScore>0 and SwoogleScore<0.6):
	    	SwoogleScaledScore = 1
	    elif(SwoogleScore>=0.6 and SwoogleScore<0.7):
	    	SwoogleScaledScore = 2
	    elif(SwoogleScore>=0.7):
	    	SwoogleScaledScore = 3
	    else:
	    	SwoogleScaledScore = 0

	    if(ESAScaledScore>SwoogleScaledScore):
	    	print("Using ESA")
	    	score = ESAScaledScore
	    else:
	    	print("Using Swoogle")
	    	score = SwoogleScaledScore

	    if(score>=2):
	    	return score
	    else:
	    	return -1
