#!/usr/bin/env python

import sys
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from pprint import pprint
from collections import defaultdict
from util import info

iii = None

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
                    print("node:")
                    # print(node.explain())
                    print(cand.explain())
                    print(cand.synonym.explain())
                    must.append(cand.binding())
                    nodesMentioned.append(cand.binding())
                    # required[truenodeDesig(cand.referent)].append(cand)
                    for w in a["words"]:
                        touches[w].add(cand)
                elif cand.referentType == 'edge':
                    edgesMentioned.append(cand.binding())
                    # required[truenodeDesig(cand.referent)].append(cand)
                    for w in a["words"]:
                        touches[w].add(cand)
        # now we have all known candidates
        for term in self.query.terms:
            if not touches[term]:
                should.append(("match", term))
        i["touches"] = touches
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
        pprint(self.intermediate(), file)
