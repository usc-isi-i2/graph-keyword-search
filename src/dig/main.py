#!/usr/bin/env python

import sys, os
import argparse

from graph import htGraph, ImpossibleGraph, minimalSubgraph
from query import Query
from synonym import Thesaurus
# from outline import Outline, iii
from outline import *
import configparser

from pprint import pprint

g = None
q = None
s = None
m = None
wg = None
sg = None
o = None

def interpretConfig(configFile, verbose=False):
    try:
        cfg = configparser.ConfigParser()
        cfg.read(configFile)
    except:
        if verbose:
            print("Unable to read any configuration from {}".format(configFile), file=sys.stderr)
    kwargs = {}
    for sectionName in cfg.sections():
        section = cfg[sectionName]
        for key, value in section.items():
            kw = sectionName + '_' + key
            try:
                if key.endswith('count') or key.endswith('size') or key.endswith('length'):
                    kwargs[kw] = section.getint(key)
                elif key.endswith('factor') or key.endswith('score'):
                    kwargs[kw] = section.getfloat(key)
                elif key.endswith('enable'):
                    kwargs[kw] = section.getboolean(key)
                else:
                    kwargs[kw] = value
            except:
                kwargs[kw] = value
    return kwargs


def main(argv=None):
    '''this is called if run from command line'''
    global g, q, s, m, wg, sg, o
    parser = argparse.ArgumentParser()
    parser.add_argument('terms', nargs='*', default=[], action="append")
    parser.add_argument('-v', '--verbose', required=False, help='verbose', action='store_true')
    parser.add_argument('-e', '--explain', required=False, help='include explanations in intermediate repn',
                        choices=['text','structured','None'])
    # parser.add_argument('-o', '--options')
    parser.add_argument('-j', '--config', required=False, help='config', default=os.path.join(os.path.dirname(__file__), "config.ini"))
    args = parser.parse_args()
    # TODO nargs generates a list of lists
    terms = args.terms[0]
    cmdline = {"verbose": args.verbose,
               "explain": None if args.explain=='None' else args.explain}
    config = interpretConfig(args.config)
    s = Thesaurus(**cmdline, **config)
    roots = ['WebPage', 'Offer', 'AdultService', 'EmailAddress', 'PhoneNumber', 'PersonOrOrganization']
    for root in roots:
        print("#" * 66)
        print("Rooted at {}".format(root))
        g = htGraph(root, **cmdline, **config)
        if not g:
            continue
        print("Root: {} yields net graph {}".format(root, g))
        q = Query(terms, g, s, **cmdline, **config)
        q.suggestCandidates()
        # q.dump()
        try:
            # m is steiner tree
            # wg is input nondirected graph
            # sg is output directed subgraph
            (m, wg, sg) = minimalSubgraph(g, root, q)
            o = Outline(g, sg, q, root, **cmdline, **config)
        except ImpossibleGraph as ig:
            if args.verbose:
                # print(ig, file=sys.stderr)
                print("It is not possible to generate a subgraph with root {}".format(root), file=sys.stderr)
            continue
        o.detail()

# call main() if this is run as standalone
if __name__ == "__main__":
    sys.exit(main())
