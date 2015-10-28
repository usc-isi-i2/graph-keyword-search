#!/usr/bin/env python

import sys
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from pprint import pprint
from collections import defaultdict

iii = None

class Outline(object):
    def __init__(self, graph, subgraph, query, root, **kwargs):
        self.graph = graph
        self.subgraph = subgraph
        self.query = query
        self.root = root

    def intermediate(self):
        global iii
        i = defaultdict(list)
        i["root"] = self.root
        # to begin with, no terms are covered
        covered = dict([(term, set()) for term in self.query.terms])
        for a in self.query.ngrams.values():
            for cand in a["candidates"]:
                if cand.referentType == 'node':
                    i["must"].append(cand.binding())
                    # required[truenodeDesig(cand.referent)].append(cand)
                    for w in a["words"]:
                        covered[w].add(cand)
                elif cand.referentType == 'edge':
                    i["must"].append(cand.binding())
                    # required[truenodeDesig(cand.referent)].append(cand)
                    for w in a["words"]:
                        covered[w].add(cand)
        # now we have all known candidates
        for term in self.query.terms:
            if not covered[term]:
                i["should"].append(("match", term))
        i["covered"] = covered
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
