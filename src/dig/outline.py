#!/usr/bin/env python

import sys
from collections import defaultdict
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
    def __init__(self, graph, subgraph, query, root, verbose=False, explain=False, **kwargs):
        self.graph = graph
        self.subgraph = subgraph
        self.query = query
        self.root = root
        self.verbose = verbose
        self.explain = explain

    def intermediate(self):
        global iii
        relationsMentioned = []
        classesMentioned = []
        must = []
        should = []
        i = defaultdict(list)
        i["root"] = self.root
        # to begin with, no terms are covered
        touches = defaultdict(list)
        for a in self.query.ngrams.values():
            for cand in a["candidates"]:
                if cand.referentType == 'node':
                    node = cand.referent
                    if self.graph.isLeaf(node):
                        # Leaf node corresponds to an equality/fuzzy relation constraint 
                        m = {"path": pathFromRoot(self.graph, cand, node, self.root),
                             "matchType": "direct" if cand.candidateType == "direct" else "inferred",
                             # "operands": [cand.referent, cand.content],
                             "className": cand.referent.split('.')[0],
                             "relationName": cand.referent.split('.')[1],
                             "value": cand.content}
                        if self.explain:
                            m["_explanation"] = cand.explain()
                        must.append(m)
                    else:
                        # Other node corresponds to mention of a class (e.g., the word 'seller' is mentioned)
                        m = {"className": self.graph.labelInGraph(node)}
                        if self.explain:
                            m["_explanation"] = cand.explain()
                        classesMentioned.append(m)
                    # Record (possibly partial) coverage of query terms
                    for w in a["words"]:
                        t = {"term": w,
                             "foundIn": "node"}
                        if self.explain:
                            t["_explanation"] = cand.explain()
                        touches[w].append(t)
                elif cand.referentType == 'edge':
                    edge = cand.referent
                    # Edge match corresponds to mention of an edge
                    # May or may not correspond to relation constraint on that edge
                    # In future, this might mean we want result to include its class
                    m = {"className": self.graph.labelInGraph(edge[0]),
                         "relationName": self.graph.labelInGraph(edge)}
                    if self.explain:
                        m["_explanation"] = cand.explain()
                    relationsMentioned.append(m)
                    # Record (possibly partial) coverage of query terms
                    for w in a["words"]:
                        t = {"term": w,
                             "foundIn": "edge"}
                        if self.explain:
                            t["_explanation"] = cand.explain()
                        touches[w].append(t)
        # Any terms never covered are now free-text matches
        for term in self.query.terms:
            if not touches[term]:
                s = {"matchType": "free",
                     "operands": [term]}
                if self.explain:
                    s["_explanation"] = "{} uninterpretable".format(term)
                should.append(s)
                                
        i["touches"] = touches
        i["relationsMentioned"] = relationsMentioned
        i["classesMentioned"] = classesMentioned
        i["must"] = must
        i["should"] = should
        iii = i
        return i

    def detail(self, file=sys.stdout):
        # print (root,g,q,s,m,wg,sg)
        print("", file=file)
        if self.verbose:
            print("\nRoot {}".format(self.root), file=file)
            print("\nDetail of outline {}".format(self), file=file)
            print("Input Graph: {}".format(self.graph), file=file)
            print("Input Keywords: {}".format(self.query.terms), file=file)
            print("Input Keyword Coloring: \n{}".format(self.query.dumpToString(indent=2)), file=file)
            print("Relevant Subgraph: {}".format(self.subgraph), file=file)
            print("Intermediate Repn:", file=file)
        print(json.dumps(self.intermediate(), sort_keys=True, indent=4), file=file)
