from ngramsEngine import ngramsEngine
from ngramTree import *
import urllib.request
import sys


class PivotEntityRecognition:

	def __init__(self):
		a =1

def main():

	#Ask the user to input the query
	sentence = input("Enter the query : ")

	#Generate the n-grams
	ngramsEngineObj = ngramsEngine()
	listNgrams,lookupList = ngramsEngineObj.generateNGrams(sentence)

	#Start building the n-gram tree by selecting the root node 
	rootWord = listNgrams[0]
	rootNode = Node(rootWord)


	#Construct the tree with the root node
	treeObj = NgramTree(rootNode)
	treeObj.constructTree(listNgrams,lookupList)

	#Make use of the spotlight to get the pivot entity

if __name__ == '__main__':
	main()




