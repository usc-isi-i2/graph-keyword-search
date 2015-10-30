#!/usr/bin/env python

import sys
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from pprint import pprint
from collections import defaultdict
from util import info
from networkx import shortest_path
import json

iii = None

def pathFromRoot(graph, cand, node, root):
    nodes = shortest_path(graph, root, node)
    pathComponents = [root]
    waypoints = nodes[0:-1]
    for (f,t) in zip(waypoints, waypoints[1:]):
        pathComponents.append(graph.labelInGraph((f,t)) or "missing")
    # pathComponents.append(nodes[-1].upper())
    # terminus is a leaf node, named after class plus relation
    # we only want the relation
    pathComponents.append(node.split('.')[-1])  
    path = ".".join(pathComponents)
    return path

class Outline(object):
    def __init__(self, graph, subgraph, query, root, **kwargs):
        self.graph = graph
        self.subgraph = subgraph
        self.query = query
        self.root = root

    def intermediate(self):
        global iii
        relationsMentioned = []
        classesMentioned = []
        must = []
        should = []
        i = defaultdict(list)
        i["root"] = self.root
        # to begin with, no terms are covered
        # touches = dict([(term, set()) for term in self.query.terms])
        touches = defaultdict(list)
        for a in self.query.ngrams.values():
            for cand in a["candidates"]:
                if cand.referentType == 'node':
                    node = cand.referent
                    if self.graph.isLeaf(node):
                        # Leaf node corresponds to an equality/fuzzy relation constraint 
                        must.append( {"path": pathFromRoot(self.graph, cand, node, self.root),
                                      "matchType": "direct" if cand.candidateType == "direct" else "fuzzy",
                                      "operands": [cand.referent, cand.content],
                                      "_explanation": cand.explain() } )
                    else:
                        # Other node corresponds to mention of a class (e.g., the word 'seller' is mentioned)
                        classesMentioned.append( {"className": self.graph.labelInGraph(node),
                                                  "_explanation": cand.explain() })
                    # Record (possibly partial) coverage of query terms
                    for w in a["words"]:
                        touches[w].append(cand.explain())
                elif cand.referentType == 'edge':
                    edge = cand.referent
                    # Edge match corresponds to mention of an edge
                    # May or may not correspond to relation constraint on that edge
                    # In future, this might mean we want result to include its class
                    relationsMentioned.append( {"className": self.graph.labelInGraph(edge[0]),
                                                "relationName": self.graph.labelInGraph(edge),
                                                "_explanation": cand.explain() } )
                    # Record (possibly partial) coverage of query terms
                    for w in a["words"]:
                        touches[w].append(cand.explain())
        # Any terms never covered are now free-text matches
        for term in self.query.terms:
            if not touches[term]:
                should.append( {"matchType": "free",
                                "operands": [term],
                                "_explanation": "{} uninterpretable".format(term) })
        # Set values converted to list in case we want to serialize to JSON
#         pprint(touches)
#         i["touches"] = {k:list(s) for (k,s) in touches.items()}
#         print(type(i["touches"]))
        i["touches"] = touches
        i["relationsMentioned"] = relationsMentioned
        i["classesMentioned"] = classesMentioned
        i["must"] = must
        i["should"] = should
        iii = i
        return i

    def detail(self, file=sys.stdout):
        # print (root,g,q,s,m,wg,sg)
        print("\nDetail of outline {}".format(self), file=file)
        print("Input Graph: {}".format(self.graph), file=file)
        print("Input Keywords: {}".format(self.query.terms), file=file)
        print("Input Keyword Coloring: \n{}".format(self.query.dumpToString(indent=2)), file=file)
        print("Relevant Subgraph: {}".format(self.subgraph), file=file)
        print("Intermediate Repn:", file=file)
        print(json.dumps(self.intermediate(), sort_keys=True, indent=4), file=file)
