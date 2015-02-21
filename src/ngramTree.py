from ngramsEngine import ngramsEngine

# This class represents Node of the tree
# A Node has value/data and also has links to its children stored as a list
class Node(object):

    def __init__(self, data):
        self.data = data
        self.children = []

    #Used to add child node to current node    
    def add_child(self, obj):
        self.children.append(obj)


# This represents a n-gram tree
class NgramTree(object):

	def __init__(self,rootNode):
		self.rootNode = rootNode


	def printNode(self,node):
		if node is None:
			return
	
		print(node.data)

		for c in node.children:
			self.printNode(c)



	# This module builds the n-gram tree with the basic idea of BFS traversal
	# Input : List1, List2
	# List1 : ['a b c d', 'a b c', 'b c d', 'a b', 'b c', 'c d', 'a', 'b', 'c', 'd']
	# List2 : [['a', 'b', 'c', 'd'], ['a b', 'b c', 'c d'], ['a b c', 'b c d'], ['a b c d']]
	# Algorithm :
	# while(queue):
	#	CurrentNode = queue.pop()
	#	search for tokens that have a length = length(CurrentNode.value) - 1 
	#	##[Get this from List2]
	#	##[These tokens will be the nodes at the next level in the tree]
	#	check if the tokens are already in the tree
	#	if not create new node with these tokens 
	#	add the token nodes as the children of CurrentNode

	def constructTree(self,listNgrams,lookupList):
		
		# This dictionary is used to track the nodes that are in the tree
		# key:Nodevalue  value:Node
		treeDictionary = {}

		# This list exhibits behaviour of a Queue
		nodeQueue = []

		#Add the root node to the Queue to begin search
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

		self.printNode(self.rootNode)


def main():
	ngramsEngineObj = ngramsEngine()
	listNgrams,lookupList = ngramsEngineObj.generateNGrams('a b c d')

	rootWord = listNgrams[0]
	rootNode = Node(rootWord)

	treeObj = NgramTree(rootNode)
	treeObj.constructTree(listNgrams,lookupList)



if __name__ == '__main__':
	main()