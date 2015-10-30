#!/usr/bin/env python

import sys
from itertools import count
from synonym import Thesaurus, Synonym
from collections import Counter
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from util import canonList

class Candidate(object):
    def __init__(self, referent=None, referentType=None, candidateType=None, synonym=None, distance=0):
        # referent is something in the graph: a node or edge, which for us is a string or tuple of strings
        self.referent = referent
        # referentType is 'node' or 'edge'
        self.referentType = referentType
        # candidateType is 'direct', 'levenshtein', 'hybridJaccard', 'synonym'
        # candidateType is 'direct', 'levenshtein', 'hybridJaccard', 'word2vec', 'wordnet'
        self.candidateType = candidateType
        self.synonym = synonym
        # distance = 0 for direct
        # presumably distance > 0 for non-direct
        self.distance = distance

    @property
    def indicator(self):
        try:
            return self.synonym and self.synonym.indicator
        except:
            return None

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
        prefix = "Cand"
        try:
            if self.candidateType=='direct':
                return "{}: {} {}: Direct({})".format(prefix, self.referentType, self.referentsLabel(), self.indicator)
            elif self.candidateType=='levenshtein':
                return "{}: {} {}: Levenshtein({})={}".format(prefix, self.referentType, self.referent, self.synonym, self.distance)
            elif self.candidateType=='hybridJaccard':
                return "{}: {} {}: HybridJaccard({})".format(prefix, self.referentType, self.referent, self.synonym)
            elif self.candidateType=='wordnet':
                s = self.synonym
                return "{}: {} {}: Wordnet({},{})=>{}".format(prefix, self.referentType, self.referent, s.source, s.indicator, s.content)
            elif self.candidateType=='word2vec':
                s = self.synonym
                return "{}: {} {}: Word2vec({},{})=>{}".format(prefix, self.referentType, self.referent, s.source, s.indicator, s.content)
        except:
            pass
        return str(self)

    def binding(self):
        # return "Binding of indicator {} is content {}".format(self.indicator, self.content)
        return (self.candidateType, self.indicator, self.content)

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
                            synonym = Synonym(source='direct', indicator=keyword, content=keyword, score=1.0)
                            d["candidates"].append(Candidate(referent=node, referentType='node', candidateType='direct', synonym=synonym))
                    # singleton, direct edge
                    for edge in graph.edges():
                        if graph.edgeMatch(edge, keyword):
                            synonym = Synonym(source='direct', indicator=keyword, content=keyword, score=1.0)
                            d["candidates"].append(Candidate(referent=edge, referentType='edge', candidateType='direct', synonym=synonym))
                
                # singleton, levenshtein node
                if self.levenshtein_enable:
                    for node in graph.nodes():
                        try:
                            (closest, away) = graph.nodeEditWithin(node, keyword, levenshteinWithin, above=levenshteinAbove)
                            synonym = Synonym(source='levenshtein', indicator=keyword, content=closest, score=away)
                            d["candidates"].append(Candidate(referent=node, referentType='node', candidateType='levenshtein', distance=away, synonym=synonym))
                        except TypeError:
                            pass
                    # singleton, levenshtein edge
                    for edge in graph.edges():
                        try:
                            (closest,away) = graph.edgeEditWithin(edge, keyword, levenshteinWithin, above=levenshteinAbove)
                            synonym = Synonym(source='levenshtein', indicator=keyword, content=closest, score=away)
                            d["candidates"].append(Candidate(referent=edge, referentType='edge', candidateType='levenshtein', distance=away, synonym=synonym))
                        except TypeError:
                            pass                
                # singleton, hybrid jaccard node
                if self.hybridjaccard_enable:
                    for node in graph.nodes():
                        best = graph.nodeNearMatch(node, keyword, allowExact=hybridJaccardAllowExact)
                        if best:
                            synonym = Synonym(source='hybridJaccard', indicator=keyword, content=best)
                            d["candidates"].append(Candidate(referent=node, referentType='node', candidateType='hybridJaccard', synonym=synonym))
                    # singleton, hybrid jaccard edge
                    for edge in graph.edges():
                        best = graph.edgeNearMatch(edge, keyword, allowExact=hybridJaccardAllowExact)
                        synonym = Synonym(source='hybridJaccard', indicator=keyword, content=best)
                        if best:
                            d["candidates"].append(Candidate(referent=edge, referentType='edge', candidateType='hybridJaccard', synonym=synonym))

                # singleton, synonym
                if self.thesaurus:
                    for synonym in thesaurus.generateSynonyms(keyword):
                        content = synonym.content
                        # singleton, synonym node
                        for node in graph.nodes():
                            if graph.nodeMatch(node, content):
                                d["candidates"].append(Candidate(referent=node, referentType='node', candidateType=synonym.source, synonym=synonym))
                        # singleton, synonym edge
                        for edge in graph.edges():
                            if graph.edgeMatch(edge, content):
                                d["candidates"].append(Candidate(referent=edge, referentType='edge', candidateType=synonym.source, synonym=synonym))

            # MULTIWORD
            elif d["cardinality"] >= 2:
                if self.direct_enable:
                    # multiword, direct
                    for node in graph.nodes():
                        if graph.nodeMatch(node, keyword):
                            synonym = Synonym(source='direct', indicator=keyword, content=keyword, score=1.0)
                            d["candidates"].append(Candidate(referent=node, referentType='node', candidateType='direct', synonym=synonym))
                    for edge in graph.edges():
                        if graph.edgeMatch(edge, keyword):
                            synonym = Synonym(source='direct', indicator=keyword, content=keyword, score=1.0)
                            d["candidates"].append(Candidate(referent=edge, referentType='edge', candidateType='direct', synonym=synonym))
                # TODO: multiword, levenshtein (or jaro_winkler, hj)
                # NIY               
                # multiword, synonym
                for synonym in thesaurus.generateSynonyms(keyword):
                    content = synonym.content
                    for node in graph.nodes():
                        if graph.nodeMatch(node, synonym):
                            d["candidates"].append(Candidate(referent=node, referentType='node', candidateType=synonym.source, synonym=synonym))
                    for edge in graph.edges():
                        if graph.edgeMatch(edge, synonym):
                            d["candidates"].append(Candidate(referent=edge, referentType='edge', candidateType=synonym.source, synonym=synonym))

#     def initNgrams0(self, terms):
#         self.ngrams = {}
#         for term,idx in zip(terms, count(0,2)):
#             # print("Term 1 {}".format(term))
#             # print("Assign spot {} to unigram {}".format(idx,term))
#             self.ngrams[term] = None
#             self.ngrams[term] = {"term": term,
#                                   "words": [term],
#                                   "index": idx,
#                                   "cardinality": 1}
#         for t1,t2,idx in zip(terms, terms[1:], count(1,2)):
#             term = t1 + "_" + t2
#             # print("Assign spot {} to bigram {}".format(idx, term))            
#             self.ngrams[term] = {"term": term,
#                                   "words": [t1, t2],
#                                   "index": idx,
#                                   "cardinality": 2}
            
#     def dump0(self):
#         byIndex = [None] * (2*len(self.terms) - 1)
#         for d in self.ngrams.values():
#             byIndex[d['index']] = d
#         for d in byIndex:
#             try:
#                 idx = d['index']
#                 ngramType = "unigram" if idx%2 else "bigram"
#                 q = d.get('term', '')
#                 v = d.get('candidates', [])
#                 # print("{}{}. {}: {}".format("  " if idx%2 else "", idx, q, "\n".join(v)))
#                 # print("{}{}. {}: {}".format("  " if idx%2 else "", idx, q, "{} candidates".format(len(v))))
#                 summaries = Counter([c.summary() for c in v])
#                 # print("{}{}. {}: {} ({})".format("  " if idx%2 else "", idx, q, "{} candidates".format(len(v))," unknown"))  
#                 print("{}{}. {}: {} ({})".format(ngramType, idx, q, "{} candidates".format(len(v)), summaries))
#             except:
#                 print(d)
                
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
