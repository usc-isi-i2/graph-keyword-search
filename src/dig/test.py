#!/usr/bin/env python

from networkx import *

g=Graph()
g.add_node('a')
g.add_node('b')
g.add_node('c')
g.add_node('d')
g.add_node('e')
g.add_node('f')
g.add_node('g')
g.add_node('h')
g.add_node('i')
g.add_node('j')
g.add_node('k')

g.add_edge('a','b', weight=1)
g.add_edge('a','c', weight=2)
g.add_edge('b','d', weight=1)
g.add_edge('c','d', weight=2)
g.add_edge('c','e', weight=1)
g.add_edge('d','f', weight=2)
g.add_edge('f','g', weight=1)
g.add_edge('d','h', weight=2)
g.add_edge('h','i', weight=1)
g.add_edge('h','j', weight=2)
g.add_edge('h','k', weight=1)
# cycle
g.add_edge('b','a', weight=1)
