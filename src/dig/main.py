#!/usr/bin/env python

import sys
import argparse

from graph import htGraph, ImpossibleGraph
from query import Query
from synonym import Thesaurus
from graph import minimalSubgraph
import pprint

g = None
q = None
s = None
m = None
wg = None
sg = None

def main(argv=None):
    '''this is called if run from command line'''
    global g, q, s, m, wg, sg
    parser = argparse.ArgumentParser()
    parser.add_argument('terms', nargs='*', default=[], action="append")
    parser.add_argument('-v','--verbose', required=False, help='verbose', action='store_true')
    parser.add_argument('-o', '--options')
    args = parser.parse_args()
    # TODO nargs generates a list of lists
    terms = args.terms[0]
    g = htGraph()
    print("Terms: {}".format(terms))
    s = Thesaurus(word2vec=True, wordnet=True)
    q = Query(terms, g, s)
    q.suggestCandidates()
    q.dump()
    # succeeds with roots = ['offer']
    # fails with roots = ['phone']
    roots = ['seller', 'phone', 'email', 'offer', 'adultservice', 'webpage']
    for root in roots:
        print("\nRoot {}".format(root))
        try:
            (m, wg, sg) = minimalSubgraph(g, root, q)
            # print (root,g,q,s,m,wg,sg)
            print("Subgraph")
            pprint.pprint(sg.nodes())
        except ImpossibleGraph as ig:
            print(ig, file=sys.stderr)

# call main() if this is run as standalone
if __name__ == "__main__":
    sys.exit(main())
