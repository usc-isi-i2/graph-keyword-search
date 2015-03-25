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

# Method that prints the initial color assigned
def printColors(treeObj,rootNode):

	# Reset the visited flag for the traversal 
	treeObj.resetVisitedFlag(rootNode)
	listNgrams = []
	stack = []
	stack.append(rootNode)

	while(stack):
		currNode = stack.pop()
		if not currNode.isVisited:
			currNode.isVisited = True	
			#print('---------')
			listNgrams.append(currNode.data)
			#print(currNode.data)
			#print(currNode.color)
			for childNodes in currNode.children:
				stack.append(childNodes)
	return listNgrams

# Print the Pivot entities recogised
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

# Print factnodes
def printTriplets(tripleList):
	for triple in tripleList:
		print('----')
		obj = triple.object
		print(str(obj.score))
		print(str(obj.colors))
		print(str(obj.keyword))
		print(str(triple.subject.uri) + ' ' + str(triple.predicate.uri) + ' ' + str(triple.object.uri))




# Gets the bigrams from the sentence and returns the bigrams that are to be covered
def getBiGramList(sentence,resource):

	sentenceList = sentence.split(' ')
	resourceKeyword = resource.keyword.split(' ')

	# remove the bigrams that has 
	for key in resourceKeyword:
		sentenceList.remove(key)

	biGramList = []

	# Form the bigrams
	if(len(sentenceList)!=0):
		for i in range(0,len(sentenceList)-1):
			biGramList.append(sentenceList[i]+' '+sentenceList[i+1])

	return biGramList


# Ranks the results coverage first followed by the scores
def rankResults(listFactNodes,length):
	# new list will contain lists of nodes with each list at index corresponding to the number of colors covered by the node
	newList = []
	
	# initialize the list
	for i in range(0,length):
		newList.append([])

	# insert the nodes at the appropriate index lists
	for node in listFactNodes:
		index = int(len(node.colors)-1)
		newList[index].append(node)

	# sort list on scores
	for list in newList:
		list.sort(key=lambda x: x.score, reverse=True)

	# flatten the sorted list
	returnList = []
	for i in range(len(newList)-1,-1,-1):
		for node in newList[i]:
			returnList.append(node)

	return returnList



# Driver method
def main():

	# Ask the user to input the query
	sentence = input("Enter the query : ")

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
	#print(printColors(treeObj,rootNode))
	print('Completed initial color assignment')
	#exit(3)
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
	print()

	# get the initial fact nodes
	listFactNodes = []
	for resource in resourceList :
		# Get the bi-gram list 
		biGramList = getBiGramList(sentence,resource)
		listFactNodes.extend(SparqlClient.getAllTripletsForPivotElement(resource,biGramList))
	
	
	for factNode in listFactNodes:
		print()
		if(factNode.isExplored == False and factNode.object.isUri):
			biGramList = getBiGramList(sentence,factNode.object)
			listFactNodes.extend(SparqlClient.getAllTripletsForPivotElement(factNode.object,biGramList))
	
	resultsList = rankResults(listFactNodes,len(sentence.split(' ')))
	
	printTriplets(resultsList)

if __name__ == '__main__':
	main()




