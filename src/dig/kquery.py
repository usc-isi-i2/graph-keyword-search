#!/usr/bin/env python

import sys
from itertools import count
from synonym import Thesaurus

class Candidate(object):
    def __init__(self, referent=None, referentType=None, candidateType=None, synonym=None, distance=None):
        self.referent = referent
        self.referentType = referentType
        self.candidateType = candidateType
        self.synonym = synonym
        self.distance = distance
        
    def __str__(self, *args, **kwargs):
        sig = "None"
        try:
            sig = (self.referentType or "")
            sig += " "
            sig += (self.candidateType or "")
            sig += " " 
            sig += (str(self.referent) or "")
            sig += " "
            sig += (str(getattr(self,"synonym",None) or ""))
        except Exception as _:
            pass
        return "<" + str(type(self).__name__) + " " + sig + ">"
    
    def __repr__(self, *args, **kwargs):
        return self.__str__(*args, **kwargs)

class Query(object):
    def __init__(self, terms, graph, thesaurus=None):
        self.terms = terms
        self.graph = graph
        self.thesaurus = thesaurus or Thesaurus()
        self.initNgrams(terms)
        
    def __str__(self, *args, **kwargs):
        limit = 4
        sig = "None"
        try:
            sig = " ".join(self.terms[0:limit]) + "..."
        except Exception as _:
            pass
        return "<" + str(type(self).__name__) + " " + sig + ">"
    
    def __repr__(self, *args, **kwargs):
        return self.__str__(*args, **kwargs)
        
    def initNgrams(self, terms):
        self.ngrams = {}
        for term,idx in zip(terms, count(0,2)):
            # print("Term 1 {}".format(term))
            # print("Assign spot {} to unigram {}".format(idx,term))
            self.ngrams[term] = None
            self.ngrams[term] = {"term": term,
                                  "words": [term],
                                  "index": idx,
                                  "cardinality": 1}
        for t1,t2,idx in zip(terms, terms[1:], count(1,2)):
            term = t1 + "_" + t2
            # print("Assign spot {} to bigram {}".format(idx, term))            
            self.ngrams[term] = {"term": term,
                                  "words": [t1, t2],
                                  "index": idx,
                                  "cardinality": 2}
            
    def suggestCandidates(self):
        # singletons only
        graph = self.graph
        ngrams = self.ngrams
        thesaurus = self.thesaurus
        # levenshtein config
        levensteinWithin = 1
        levenshteinAbove = 0
        # hybrid jaccard config
        hybridJaccardAllowExact = False

        for k,d in ngrams.items():
            keyword = k
            d["candidates"] = []
            if d["cardinality"] == 1:
                # singleton, direct node
                for node in graph.nodes():
                    if graph.nodeMatch(node, keyword):
                        d["candidates"].append(Candidate(referent=node, referentType='node', candidateType='direct'))
                # singleton, direct edge
                for edge in graph.edges():
                    if graph.edgeMatch(edge, keyword):
                        d["candidates"].append(Candidate(referent=edge, referentType='edge', candidateType='direct'))
                
                # singleton, levenshtein node
                for node in graph.nodes():
                    away = graph.nodeEditWithin(node, keyword, levensteinWithin, above=levenshteinAbove)
                    if away:
                        d["candidates"].append(Candidate(referent=node, referentType='node', candidateType='levenshtein', distance=away))
                # singleton, levenshtein edge
                for edge in graph.edges():
                    away = graph.edgeEditWithin(edge, keyword, levensteinWithin, above=levenshteinAbove)
                    if away:
                        d["candidates"].append(Candidate(referent=edge, referentType='edge', candidateType='levenshtein', distance=away))
                
                # singleton, hybrid jaccard node
                for node in graph.nodes():
                    best = graph.nodeNearMatch(node, keyword, allowExact=hybridJaccardAllowExact)
                    if best:
                        d["candidates"].append(Candidate(referent=node, referentType='node', candidateType='hybridJaccard', synonym=best))
                # singleton, hybrid jaccard edge
                for edge in graph.edges():
                    best = graph.edgeNearMatch(edge, keyword, allowExact=hybridJaccardAllowExact)
                    if best:
                        d["candidates"].append(Candidate(referent=edge, referentType='edge', candidateType='hybridJaccard', synonym=best))
                                         
                # singleton, synonym
                for s in thesaurus.generateSynonyms(keyword):
                    target = s.target
                    # singleton, synonym node
                    for node in graph.nodes():
                        if graph.nodeMatch(node, target):
                            d["candidates"].append(Candidate(referent=node, referentType='node', candidateType='synonym', synonym=s))
                    # singleton, synonym edge
                    for edge in graph.edges():
                        if graph.edgeMatch(edge, target):
                            d["candidates"].append(Candidate(referent=edge, referentType='edge', candidateType='synonym', synonym=s))
            elif d["cardinality"] >= 2:
                # multiword, direct
                for node in graph.nodes():
                    if graph.nodeMatch(node, keyword):
                        d["candidates"].append(Candidate(referent=node, referentType='node', candidateType='direct'))
                for edge in graph.edges():
                    if graph.edgeMatch(edge, keyword):
                        d["candidates"].append(Candidate(referent=edge, referentType='edge', candidateType='direct'))
                # multiword, levenshtein or jaro_winkler
                # multiword, synonym
                for s in thesaurus.generateSynonyms(keyword):
                    syn = s.target
                    for node in graph.nodes():
                        if graph.nodeMatch(node, syn):
                            d["candidates"].append(Candidate(referent=node, referentType='node', candidateType='synonym', synonym=syn))
                    for edge in graph.edges():
                        if graph.edgeMatch(edge, syn):
                            d["candidates"].append(Candidate(referent=edge, referentType='edge', candidateType='synonym', synonym=syn))
    
    def dump(self):
        byIndex = [None] * (2*len(self.terms) - 1)
        for d in self.ngrams.values():
            byIndex[d['index']] = d
        for d in byIndex:
            try:
                idx = d['index']
                k = d.get('term', '')
                v = d.get('candidates', [])
                print("{}{}. {}: {}".format("  " if idx%2 else "", idx, k, v))
            except:
                print(d)
