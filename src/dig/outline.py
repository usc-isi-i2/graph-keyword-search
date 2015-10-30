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
        edgesMentioned = []
        nodesMentioned = []
        must = []
        should = []
        i = defaultdict(list)
        i["root"] = self.root
        # to begin with, no terms are covered
        touches = dict([(term, set()) for term in self.query.terms])
        for a in self.query.ngrams.values():
            for cand in a["candidates"]:
                if cand.referentType == 'node':
                    node = cand.referent
                    if self.graph.isLeaf(node):
                        must.append( {"path": pathFromRoot(self.graph, cand, node, self.root),
                                      "matchType": "direct" if cand.candidateType == "direct" else "fuzzy",
                                      "operands": [cand.referent, cand.content],
                                      "_explanation": cand.explain() } )
                    else:
                        nodesMentioned.append( {"className": self.graph.labelInGraph(node),
                                                "_explanation": cand.explain() })
                    for w in a["words"]:
                        touches[w].add(cand.explain())
                elif cand.referentType == 'edge':
                    edge = cand.referent
                    # print("edge: {}".format("leaf" if self.graph.isLeaf(edge) else "nonleaf"))
                    edgesMentioned.append( {"className": self.graph.labelInGraph(edge[0]),
                                            "relationName": self.graph.labelInGraph(edge),
                                            "_explanation": cand.explain() } )
                                          
                    # required[truenodeDesig(cand.referent)].append(cand)
                    for w in a["words"]:
                        touches[w].add(cand.explain())
        # now we have all known candidates
        for term in self.query.terms:
            if not touches[term]:
                should.append(("match", term))
        # Set values converted to list in case we want to serialize to JSON
        pprint(touches)
        i["touches"] = {k:list(s) for (k,s) in touches.items()}
        print(type(i["touches"]))
        i["edgesMentioned"] = edgesMentioned
        i["nodesMentioned"] = nodesMentioned
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
