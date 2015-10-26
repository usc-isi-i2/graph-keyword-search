#!/usr/bin/env python

import sys
import argparse

from graph import htGraph, ImpossibleGraph
from kquery import KQuery
from synonym import Thesaurus
from graph import minimalSubgraph

g = None
k = None
s = None
m = None
wg = None
sg = None

def main(argv=None):
    '''this is called if run from command line'''
    global g, k, s, m, wg, sg
    parser = argparse.ArgumentParser()
    parser.add_argument('terms', nargs='*', default=[], action="append")
    parser.add_argument('-v','--verbose', required=False, help='verbose', action='store_true')
    args = parser.parse_args()
    # nargs generates a list of lists, research this
    terms = args.terms[0]
    g = htGraph()
    print("Terms: {}".format(terms))
    s = Thesaurus()
    k = KQuery(terms, g, s)
    k.suggestCandidates()
    # succeeds with roots = ['offer']
    roots = ['offer']
    # fails with roots = ['phone']
    roots = ['phone']
    roots = ['seller', 'phone', 'email', 'offer', 'adultservice', 'webpage']
    for root in roots:
        print("\nRoot {}".format(root))
        try:
            (m, wg, sg) = minimalSubgraph(g, root, k)
            print (root,g,k,s,m,wg,sg)
        except ImpossibleGraph as ig:
            print(ig, file=sys.stderr)

# call main() if this is run as standalone
if __name__ == "__main__":
    sys.exit(main())
