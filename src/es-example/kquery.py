#!/usr/bin/env python

import sys
from itertools import count
from synonym import SynonymGenerator

class Candidate(object):
    def __init__(self, referent=None, referentType=None, candidateType=None, synonym=None):
        self.referent = referent
        self.referentType = referentType
        self.candidateType = candidateType
        self.synonym = synonym
        
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

class KQuery(object):
    def __init__(self, terms, graph, synonymGenerator):
        self.terms = terms
        self.graph = graph
        self.synonymGenerator = synonymGenerator or SynonymGenerator()
        self.initAnchors(terms)
        
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
        
    def initAnchors(self, terms):
        self.anchors = {}
        for term,idx in zip(terms, count(0,2)):
            print("Term 1 {}".format(term))
            print("Assign spot {} to unigram {}".format(idx,term))
            self.anchors[term] = None
            self.anchors[term] = {"term": term,
                                  "words": [term],
                                  "index": idx,
                                  "cardinality": 1}
        for t1,t2,idx in zip(terms, terms[1:], count(1,2)):
            term = t1 + "_" + t2
            print("Assign spot {} to bigram {}".format(idx, term))            
            self.anchors[term] = {"term": term,
                                  "words": [t1, t2],
                                  "index": idx,
                                  "cardinality": 2}
            
    def suggestCandidates(self):
        # singletons only
        graph = self.graph
        anchors = self.anchors
        within = 1
        sg = self.synonymGenerator
        for k,d in anchors.items():
            keyword = k
            d["candidates"] = []
            if d["cardinality"] == 1:
                # singleton, direct
                for node in graph.nodes():
                    if graph.nodeMatch(node, keyword):
                        d["candidates"].append(Candidate(referent=node, referentType='node', candidateType='direct'))
                for edge in graph.edges():
                    if graph.edgeMatch(edge, keyword):
                        d["candidates"].append(Candidate(referent=edge, referentType='edge', candidateType='direct'))
                # singleton, levenshtein
                for node in graph.nodes():
                    away = graph.nodeEditWithin(node, keyword, within, above=0)
                    if away:
                        d["candidates"].append(Candidate(referent=node, referentType='node', candidateType='levenshtein', distance=away))
                for edge in graph.edges():
                    away = graph.edgeEditWithin(edge, keyword, within, above=0)
                    if away:
                        d["candidates"].append(Candidate(referent=edge, referentType='edge', candidateType='levenshtein', distance=away))                
                # singleton, synonym
                for s in sg.generateSynonyms(keyword):
                    target = s.target
                    for node in graph.nodes():
                        if graph.nodeMatch(node, target):
                            d["candidates"].append(Candidate(referent=node, referentType='node', candidateType='synonym', synonym=s))
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
                for s in sg.generateSynonyms(keyword):
                    syn = s.target
                    for node in graph.nodes():
                        if graph.nodeMatch(node, syn):
                            d["candidates"].append(Candidate(referent=node, referentType='node', candidateType='synonym', synonym=syn))
                    for edge in graph.edges():
                        if graph.edgeMatch(edge, syn):
                            d["candidates"].append(Candidate(referent=edge, referentType='edge', candidateType='synonym', synonym=syn))
    
    def suggestCandidates3(self):
        # singletons only
        graph = self.graph
        anchors = self.anchors
        sg = self.synonymGenerator
        for k,d in anchors.items():
            keyword = k
            d["candidates"] = []
            if d["cardinality"] == 1:
                # singleton, direct
                for node in graph.nodes():
                    if keyword in graph.node[node]['values']:
                        d["candidates"].append(Candidate(referent=node, referentType='node', candidateType='direct'))
                for edge in graph.edges():
                    if keyword in graph.edge[edge[0]][edge[1]]['values']:
                        d["candidates"].append(Candidate(referent=edge, referentType='edge', candidateType='direct'))
                # singleton, synonym
                for s in sg.generateSynonyms(keyword):
                    syn = s.target
                    for node in graph.nodes():
                        if syn in graph.node[node]['values']:
                            d["candidates"].append(Candidate(referent=node, referentType='node', candidateType='synonym', synonym=syn))
                    for edge in graph.edges():
                        if syn in graph.edge[edge[0]][edge[1]]['values']:
                            d["candidates"].append(Candidate(referent=edge, referentType='edge', candidateType='synonym', synonym=syn))
            elif d["cardinality"] >= 2:
                pass   

 
    def dump(self):
        byIndex = [None] * (2*len(self.terms))
        for d in self.anchors.values():
            byIndex[d['index']] = d
        for d in byIndex:
            try:
                idx = d['index']
                k = d.get('term', '')
                v = d.get('candidates', [])
                print("{}{}. {}: {}".format("  " if idx%2 else "", idx, k, v))
            except:
                print(d)
