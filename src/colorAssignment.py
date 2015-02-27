from ngramTree import *

# This class is responsible for assignment of colors to the nodes in the ngram tree
class ColorAssignment:


	# lookuplist - [['a', 'b', 'c', 'd'], ['a b', 'b c', 'c d'], ['a b c', 'b c d'], ['a b c d']]
	def assignInitialColors(self,rootNode,lookupList):
		
		colorDictionary = {}	# This dictionary stores the individual tokens ['a', 'b', 'c', 'd'] and their color values
		
		if rootNode and len(lookupList)>=1:
			oneGrams = lookupList[0]	# Gets the one grams		
			
			for index in range(len(oneGrams)):	
				if(oneGrams[index] not in colorDictionary):
					colorDictionary[oneGrams[index]] = index		# This assigns the color values to each token


			stack = []
			stack.append(rootNode)									# Using stack for DFS

			while(stack):
				currNode = stack.pop()

				# Assign colors to this node based on the presence of tokens
				if not currNode.isVisited:							# If a node repeats, do not initialize color again
					
					currNode.isVisited = True						

					tokens = currNode.data.split(' ')				# Check for individual tokens
					
					for token in tokens:							
						if(token in colorDictionary):
							currNode.color.append(colorDictionary[token])	# Assign colors

					for childNodes in currNode.children:			# Add children to the stack
						stack.append(childNodes)
		

		return rootNode	






			


