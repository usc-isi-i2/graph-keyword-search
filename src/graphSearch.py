from ngramsEngine import ngramsEngine
from ngramTree import *
from spotlight import *
from colorAssignment import ColorAssignment
from sparqlClient import SparqlClient

import urllib.request
import sys


class GraphSearch:

	def __init__(self):
		a =1

def printColors(treeObj,rootNode):

	# Reset the visited flag for the traversal 
	treeObj.resetVisitedFlag(rootNode)
	
	stack = []
	stack.append(rootNode)

	while(stack):
		currNode = stack.pop()
		if not currNode.isVisited:
			currNode.isVisited = True	
			print('---------')
			print(currNode.data)
			print(currNode.color)
			for childNodes in currNode.children:
				stack.append(childNodes)
	#exit(3)

def printpre(resourceList):
	print('------------ Pivot Entity Recognition --------------')
	if(len(resourceList)==0):
		print('no pivot entity found')
	else:
		for res in resourceList:
			print('Resource name : '+res.uri)
			print("Label : "+res.label)
			print("Incoming Links :  "+str(res.support))
			print("keyword : "+res.keyword)
			print('------------------------')

def printTriplets(tripleList):
	for triple in tripleList:
		print(triple.predicate)


def main():

	# Ask the user to input the query
	sentence = input("Enter the query : ")

	# Generate the n-grams
	ngramsEngineObj = ngramsEngine()
	listNgrams,lookupList = ngramsEngineObj.generateNGrams(sentence)

	# Start building the n-gram tree by selecting the root node 
	rootWord = listNgrams[0]
	rootNode = Node(rootWord)

	# Construct the tree with the root node
	treeObj = NgramTree(rootNode)
	treeObj.constructTree(listNgrams,lookupList)
	
	# Print tree 
	#treeObj.printNode(rootNode)

	# Color assignment
	colorAssignmentObj = ColorAssignment()
	colorAssignmentObj.assignInitialColors(rootNode,lookupList)
	
	# Prints colours
	#printColors(treeObj,rootNode)
	
	# Make use of the spotlight to get the pivot entity
	spotlightObject = Spotlight()
	spotlightObject.getPivotElement(sentence)

	resourceList = spotlightObject.getPivotElement(sentence)

	#print PRE
	#printpre(resourceList)
	
	tripleList = SparqlClient.getAllTripletsForPivotElement(resourceList[0].uri)
	printTriplets(tripleList)


if __name__ == '__main__':
	main()




