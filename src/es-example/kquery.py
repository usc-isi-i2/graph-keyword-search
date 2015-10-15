#!/usr/bin/env python

import sys
from itertools import count
from synonym import SynonymGenerator

class Candidate(object):
    def __init__(self, referent=None, referentType=None, candidateType=None, source=None):
        self.referent = referent
        self.referentType = referentType
        self.candidateType = candidateType
        self.source = source
        
    def __str__(self, *args, **kwargs):
        sig = "None"
        try:
            sig = self.referentType or ""
            sig += " " + (sig.referent or "")
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
            print(type(term))
            self.anchors[term] = None
            self.anchors[term] = {"term": term,
                                  "words": [term],
                                  "index": idx,
                                  "cardinality": 1}
        for t1,t2,idx in zip(terms, terms[1:], count(1,3)):
            term = t1 + "_" + t2
            self.anchors[term] = {"term": term,
                                  "words": [t1, t2],
                                  "index": idx,
                                  "cardinality": 2}
            
    def suggestCandidates(self):
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
                            d["candidates"].append(Candidate(referent=node, referentType='node', candidateType='synonym', synonym=s))
                    for edge in graph.edges():
                        if syn in graph.edge[edge[0]][edge[1]]['values']:
                            d["candidates"].append(Candidate(referent=edge, referentType='edge', candidateType='synonym', synonym=s))
            elif d["cardinality"] >= 2:
                pass   
                         
    def suggestCandidates1(self):
        # singletons only
        graph = self.graph
        anchors = self.anchors
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
                for (synonym, source) in generateSynonyms(keyword):
                    for node in graph.nodes():
                        if synonym in graph.node[node]['values']:
                            d["candidates"].append(Candidate(referent=node, referentType='node', candidateType='synonym', source=source))
                    for edge in graph.edges():
                        if synonym in graph.edge[edge[0]][edge[1]]['values']:
                            d["candidates"].append(Candidate(referent=edge, referentType='edge', candidateType='synonym', source=source))
            elif d["cardinality"] >= 2:
                pass            
                    
    def suggestCandidates0(self):
        # singletons only
        graph = self.graph
        anchors = self.anchors
        for k,d in anchors.items():
            keyword = k
            d["candidates"] = []
            if d["cardinality"] == 1:
                # singleton, direct
                for node in graph.nodes():
                    if keyword in graph.node[node]['values']:
                        print("D={}".format(d))
                        d["candidates"].append((node, 'node', 'direct'))
                for edge in graph.edges():
                    if keyword in graph.edge[edge[0]][edge[1]]['values']:
                        d["candidates"].append((edge, 'edge', 'direct'))
                # singleton, synonym
                for (synonym, source) in generateSynonyms(keyword):
                    for node in graph.nodes():
                        if synonym in graph.node[node]['values']:
                            d["candidates"].append((node, 'node', source))
                    for edge in graph.edges():
                        if synonym in graph.edge[edge[0]][edge[1]]['values']:
                            d["candidates"].append((edge, 'edge', source))
            elif d["cardinality"] >= 2:
                pass            
                
            
