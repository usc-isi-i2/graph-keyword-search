#!/usr/bin/env python

import sys
from itertools import count
from synonym import Thesaurus
from collections import Counter
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from util import canonList

class Candidate(object):
    def __init__(self, referent=None, referentType=None, candidateType=None, synonym=None, distance=None):
        self.referent = referent
        self.referentType = referentType
        self.candidateType = candidateType
        self.synonym = synonym
        self.distance = distance

    @property
    def indicator(self):
        return self.referent

    @property
    def content(self):
        try:
            return self.synonym and self.synonym.content
        except:
            return self.synonym
        
    def __str__(self, *args, **kwargs):
        sig = "None"
        try:
            sig = (self.referentType or "")
            sig += " "
            sig += (self.candidateType or "")
            sig += " " 
            sig += (self.referentsLabel() or "")
            sig += " "
            sig += (str(getattr(self,"synonym",None) or ""))
        except Exception as _:
            pass
        return "<" + str(type(self).__name__) + " " + sig + ">"

    def __repr__(self, *args, **kwargs):
        return self.__str__()

    def referentsLabel(self):
        return "/".join(canonList(self.referent))
    
    def summary(self):
        try:
            return self.candidateType
        except:
            return None
        
    def explain(self):
        try:
            if self.candidateType=='direct':
                return "{} {}: Direct".format(self.referentType, self.referent if isinstance(self.referent, str) else "/".join(self.referent))
            elif self.candidateType=='levenshtein':
                # return "{}: Levenshtein".format(self.referent)
                return "{} {}: Levenshtein({})={}".format(self.referentType, self.referent, self.synonym, self.distance)
            elif self.candidateType=='hybridJaccard':
                return "{} {}: HybridJaccard({})".format(self.referentType, self.referent, self.synonym)
            elif self.candidateType=='synonym':
                s = self.synonym
                return "{} {}: Synonym({},{})=>{}".format(self.referentType, self.referent, s.source, s.seed, s.target)
        except:
            pass
        return str(self)

    def binding(self):
        # return "Binding of indicator {} is content {}".format(self.indicator, self.content)
        return (self.indicator, self.content)

class Query(object):
    def __init__(self, terms, graph, thesaurus=None, 
                 direct_enable=True, 
                 levenshtein_enable=True, 
                 levenshtein_above_score=0.0,
                 levenshtein_within_score=1.0,
                 hybridjaccard_enable=True, 
                 hybridjaccard_allowexact_enable=False,
                 **kwargs):
        self.terms = terms
        self.graph = graph
        # self.thesaurus = thesaurus or Thesaurus()
        self.thesaurus = thesaurus
        self.direct_enable = direct_enable
        self.levenshtein_enable = levenshtein_enable
        self.levenshtein_above_score = levenshtein_above_score
        self.levenshtein_within_score = levenshtein_within_score
        self.hybridjaccard_enable = hybridjaccard_enable
        self.hybridjaccard_allowexact_enable = hybridjaccard_allowexact_enable
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
        levenshteinWithin = self.levenshtein_within_score
        levenshteinAbove = self.levenshtein_above_score
        # hybrid jaccard config
        hybridJaccardAllowExact = self.hybridjaccard_allowexact_enable

        for q,d in ngrams.items():
            keyword = q
            d["candidates"] = []

            # SINGLETON
            if d["cardinality"] == 1:
                # singleton, direct node
                if self.direct_enable:
                    for node in graph.nodes():
                        if graph.nodeMatch(node, keyword):
                            d["candidates"].append(Candidate(referent=node, referentType='node', candidateType='direct', synonym=keyword))
                    # singleton, direct edge
                    for edge in graph.edges():
                        if graph.edgeMatch(edge, keyword):
                            d["candidates"].append(Candidate(referent=edge, referentType='edge', candidateType='direct', synonym=keyword))
                
                # singleton, levenshtein node
                if self.levenshtein_enable:
                    for node in graph.nodes():
                        try:
                            (synonym, away) = graph.nodeEditWithin(node, keyword, levenshteinWithin, above=levenshteinAbove)
                            d["candidates"].append(Candidate(referent=node, referentType='node', candidateType='levenshtein', distance=away, synonym=synonym))
                        except TypeError:
                            pass
                    # singleton, levenshtein edge
                    for edge in graph.edges():
                        try:
                            (synonym,away) = graph.edgeEditWithin(edge, keyword, levenshteinWithin, above=levenshteinAbove)
                            d["candidates"].append(Candidate(referent=edge, referentType='edge', candidateType='levenshtein', distance=away, synonym=synonym))
                        except TypeError:
                            pass                
                # singleton, hybrid jaccard node
                if self.hybridjaccard_enable:
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
                if self.thesaurus:
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

            # MULTIWORD
            elif d["cardinality"] >= 2:
                if self.direct_enable:
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

    def initNgrams0(self, terms):
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
            
    def dump0(self):
        byIndex = [None] * (2*len(self.terms) - 1)
        for d in self.ngrams.values():
            byIndex[d['index']] = d
        for d in byIndex:
            try:
                idx = d['index']
                ngramType = "unigram" if idx%2 else "bigram"
                q = d.get('term', '')
                v = d.get('candidates', [])
                # print("{}{}. {}: {}".format("  " if idx%2 else "", idx, q, "\n".join(v)))
                # print("{}{}. {}: {}".format("  " if idx%2 else "", idx, q, "{} candidates".format(len(v))))
                summaries = Counter([c.summary() for c in v])
                # print("{}{}. {}: {} ({})".format("  " if idx%2 else "", idx, q, "{} candidates".format(len(v))," unknown"))  
                print("{}{}. {}: {} ({})".format(ngramType, idx, q, "{} candidates".format(len(v)), summaries))
            except:
                print(d)
                
    def dump(self, file=sys.stdout):
        byIndex = [None] * (2*len(self.terms) - 1)
        for d in self.ngrams.values():
            byIndex[d['index']] = d
        for d in byIndex:
            try:
                idx = d['index']
                # seems backward
                ngramType = "bigram" if idx%2 else "unigram"
                q = d.get('term', '')
                v = d.get('candidates', [])
                # print("{}{}. {}: {}".format("  " if idx%2 else "", idx, q, "\n".join(v)))
                # print("{}{}. {}: {}".format("  " if idx%2 else "", idx, q, "{} candidates".format(len(v))))
                # summaries = Counter([c.summary() for c in v])
                # print("{}{}. {}: {} ({})".format("  " if idx%2 else "", idx, q, "{} candidates".format(len(v))," unknown"))  
                print("({}) {}. {}:".format(ngramType, idx, q), file=file)
                # print("Candidates:")
                if v:
                    for c in v:
                        # print(c.summary())
                        # print(c)
                        print("  " + c.explain(), file=file)
                else:
                    print("  None", file=file)
            except:
                print(d, file=file)
        
    def dumpToString(self, indent=0):
        buffer = StringIO()
        self.dump(file=buffer)
        s = buffer.getvalue()
        buffer.close()
        prefix = " " * indent
        return (prefix + s.replace("\n", "\n" + prefix)
                if prefix
                else s)
