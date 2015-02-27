from ngramsEngine import ngramsEngine

# This class represents Node of the tree
# A Node has value/data and also has links to its children stored as a list
class Node(object):

    def __init__(self, data):
        self.data = data 			# Data in the node
        self.color = ''				# Colour assignment for the node
        self.children = []			# Represents the child nodes
        self.isDuplicate = False	# Checks if this node is the child of 2 different nodes
        self.isVisited = False		# This flag helps is traversal


    #Used to add child node to current node    
    def add_child(self, obj):
        self.children.append(obj)


# This represents a n-gram tree
class NgramTree(object):

	def __init__(self,rootNode):
		self.rootNode = rootNode

	# Post order traversal of the tree (DFS)
	def post_order(self,node):
		for n in node.children:
			self.post_order(n)

		if not node.isVisited:
			node.isVisited = True
			print(node.data)


	# BFS traversal
	def printNode(self,node):
		if node is None:
			return
		if not node.isVisited:
			node.isVisited = True
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

		nodeQueue = []											# This list exhibits behaviour of a Queue
		nodeQueue.append(self.rootNode)							# Add the root node to the Queue to begin search
		treeDictionary[self.rootNode.data] = self.rootNode		# Add the root to the treeDictionary as it is seen


		while(nodeQueue):
			currentNode = nodeQueue.pop(0)						# Pop the queue
			data = currentNode.data 							# Get the data of the node

			dataLen = len(data.split(' '))						# Get the length of the n-grams in the current token

			if(dataLen-2 >= 0):									# Stop if we have reached situation where current iteration is for individual tokens
				listChildren = lookupList[dataLen-2]			# Get the tokens that have a lenghth 1 less than that of the current token from the look up list

				for child in listChildren:						
					if child in data:							# Check if the child is a sustring of the token

						if child not in treeDictionary:			# Check if a node for 'child' is already created. If so retrieve that node and set it as a duplicate
							newNode = Node(child)
							nodeQueue.append(newNode)
							treeDictionary[child] = newNode
						else:
							newNode = treeDictionary[child]
							newNode.isDuplicate = True

						currentNode.add_child(newNode)			# Add this child to the parent node

		#self.printNode(self.rootNode)
		#self.post_order(self.rootNode)


def main(query):
	ngramsEngineObj = ngramsEngine()
	listNgrams,lookupList = ngramsEngineObj.generateNGrams(query)

	rootWord = listNgrams[0]
	rootNode = Node(rootWord)

	treeObj = NgramTree(rootNode)
	treeObj.constructTree(listNgrams,lookupList)



if __name__ == '__main__':
	main()