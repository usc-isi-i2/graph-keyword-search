from ngramsEngine import ngramsEngine
from ngramTree import *
from pivotEntityRecognition import *
from colorAssignment import ColorAssignment
from sparqlClient import SparqlClient
import inflection
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
			print("colors : "+str(res.colors))
			print('------------------------')

def printTriplets(tripleList):
	for triple in tripleList:
		print('----')
		obj = triple.object
		print(str(obj.score))
		print(str(obj.colors))
		print(str(obj.isUri))
		print(str(triple.subject.uri) + ' ' + str(triple.predicate.uri) + ' ' + str(triple.object.uri))
		
def main():

	# Ask the user to input the query
	sentence = input("Enter the query : ")
	#sentence = 'sachin tendulkar country label'
	print()
	print()
	print('Phase 1 ... N GRAM Generation')
	# Generate the n-grams
	ngramsEngineObj = ngramsEngine()
	listNgrams,lookupList = ngramsEngineObj.generateNGrams(sentence)
	print('Generated N-grams')


	# Start building the n-gram tree by selecting the root node 
	rootWord = listNgrams[0]
	rootNode = Node(rootWord)

	
	# Construct the tree with the root node
	treeObj = NgramTree(rootNode)
	treeObj.constructTree(listNgrams,lookupList)
	
	# Print tree 
	#treeObj.printNode(rootNode)
	print('N-gram tree constructed')

	print()
	print('Phase 2 ...  Color assignment')
	
	# Color assignment
	colorAssignmentObj = ColorAssignment()
	colorAssignmentObj.assignInitialColors(rootNode,lookupList)
	
	
	# Prints colours
	#printColors(treeObj,rootNode)
	print('Completed initial color assignment')
	
	print()
	print('Phase 3 ... PivotEntityRecognition')
	# Make use of the spotlight to get the pivot entities sorted on the number of incoming links
	spotlightObject = PivotEntityRecognition()
	resourceList = spotlightObject.getPivotElement(sentence)
	

	#print PRE
	#printpre(resourceList)
	print('Got the pivot element')

	print()

	
	print('Phase 4 ... Search Phase')

	# get the initial fact nodes
	listFactNodes = []
	for resource in resourceList :
		listFactNodes.extend(SparqlClient.getAllTripletsForPivotElement(resource))
	
	
	for factNode in listFactNodes:
		if(factNode.isExplored == False and factNode.object.isUri):
			listFactNodes.extend(SparqlClient.getAllTripletsForPivotElement(factNode.object))
	
	listFactNodes.sort(key=lambda x: len(x.colors), reverse=True)
	#listFactNodes.sort(key=lambda x: x.score, reverse=True)

	printTriplets(listFactNodes)

if __name__ == '__main__':
	main()




