from collections import OrderedDict

# Model class for resource elements
class Resource:
	def __init__(self,uri,label,support,keyword):		
		self.uri = uri												# URI of the resource. 
		self.label = label  										# Label of the resource
		self.support = int(support)									# Importance/ represents the number of incoming links in DBPedia on to the resource
		self.keyword = keyword										# Keyword represented by the resource
		self.colors = []											# Colors assigned
		self.score = 0
		self.isUri = False

# Fact node model class.
# Fact node is a node that represents a RDF Triple.
# In addition, we also maintain the keywords in the query that this fact node covers
class FactNode:
	def __init__(self,subject,predicate,object):
		self.subject = subject										# Subject of the fact node
		self.predicate = predicate									# Predicate
		self.object = object										# Object
		self.colors = []											# Colours
		self.children = []											# Child Nodes
		self.score = 0												# Represents the score of the the current fact node - This is a cumulative score
		self.isExplored = False										# A boolean flag to check if the currect fact node is explored during search

	# Used to add child node to current node    
	def add_child(self, obj):
		self.children.append(obj)
	
	# Set colors of the fact node from the colors of subject , predicate and object resources
    # Eg. 
    #		Fact_node triple -> dbPedia:Bill_Gates dbPedia:spouse dbPedia:Melinda_Gates 
    #		dbPedia:Bill_Gates covers colors 2,3
    #		dbPedia:spouse covers colours 1
    # 		dbPedia:Melinda_Gates covers 1,2,3

    # 		then the fact node covers 1,2,3
	def set_colors(self):
			
		for color in self.subject.colors:
			if(color not in self.colors):
				self.colors.append(color)

		for color in self.predicate.colors:
			if(color not in self.colors):
				self.colors.append(color)
		
		for color in self.object.colors:
			if(color not in self.colors):
				self.colors.append(color)

# Resource Graph Model class
# This graph will have Fact nodes as the nodes which inturn will have Resources
class ResourceGraph:
	def __init__(self,rootNode):
		self.rootNode = rootNode


