from ngramsEngine import ngramsEngine

#This class represents Node of the tree
#A Node has value/data and also has links to its children stored as a list
class Node(object):

    def __init__(self, data):
        self.data = data
        self.children = []

    #Used to add child node to current node    
    def add_child(self, obj):
        self.children.append(obj)


#This represents a n-gram tree
class NgramTree(object):

	def __init__(self,rootNode):
		self.rootNode = rootNode

	#This module builds the n-gram tree with the basic idea of BFS traversal
	def constructTree(self,listNgrams,lookupList):
		
		treeDictionary = {}
		nodeQueue = []

		nodeQueue.append(self.rootNode)
		treeDictionary[self.rootNode.data] = self.rootNode

		while(nodeQueue):
			currentNode = nodeQueue.pop(0)
			data = currentNode.data

			dataLen = len(data.replace(' ',''))

			if(dataLen-2 >= 0):
				listChildren = lookupList[dataLen-2]

				for child in listChildren:
					if child in data:
						if child not in treeDictionary:
							newNode = Node(child)
							nodeQueue.append(newNode)
						else:
							newNode = treeDictionary[child]

						currentNode.add_child(newNode)


def main():
	ngramsEngineObj = ngramsEngine()
	listNgrams,lookupList = ngramsEngineObj.generateNGrams('a b c d')

	rootWord = listNgrams[0]
	rootNode = Node(rootWord)

	treeObj = NgramTree(rootNode)
	treeObj.constructTree(listNgrams,lookupList)


if __name__ == '__main__':
	main()