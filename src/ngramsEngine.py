from nltk.util import ngrams

#This class makes use of nltk library for generating n-grams given a query
class ngramsEngine(object):

	def __init__(self):
		self = self

	# Module to print n-grams
	def printNGrams(self,ngramsList):
		for token in ngramsList:
			sen = ''
			for word in token:
				sen = sen + ' '+ word
			print(sen.strip())


	# Module that generates n-grams
	# Input : query
	# Output : list containing n-grams 
	def generateNGrams(self,query):

		ngramsList = []
		for n in range(len(query),0,-1):
			ngramsList.extend(ngrams(query.split(),n))
		return ngramsList



def main():
	ngramsEngineObject = ngramsEngine()
	query = input(" Enter the query : ")

	ngramsList = ngramsEngineObject.generateNGrams(query.strip())
	ngramsEngineObject.printNGrams(ngramsList)

if __name__ == '__main__':
	main()













