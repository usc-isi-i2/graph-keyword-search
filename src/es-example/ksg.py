#!/usr/bin/env python

import sys
import argparse

from graph import htGraph
from kquery import KQuery
from synonym import SynonymGenerator
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
#     parser.add_argument('-t','--type', 
#                         required=False, 
#                         help='domain type',
#                         default='ht')    
    parser.add_argument('-v','--verbose', required=False, help='verbose', action='store_true')
    args = parser.parse_args()
    # nargs generates a list of lists, research this
    terms = args.terms[0]
    g = htGraph()
    print("Terms: {}".format(terms))
    s = SynonymGenerator()
    k = KQuery(terms, g, s)
    k.suggestCandidates()
    (m, wg, sg) = minimalSubgraph(g, 'offer', k)
    return (g,k,s,m,wg,sg)

# call main() if this is run as standalone
if __name__ == "__main__":
    sys.exit(main())
