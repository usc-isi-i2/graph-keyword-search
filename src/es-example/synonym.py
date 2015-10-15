#!/usr/bin/env python

import sys, os

from nltk.corpus import wordnet as wn
import word2vec
from builtins import setattr

class Synonym(object):
    def __init__(self, *args, seed=None, target=None, score=1.0, **kwargs):
        self.seed = seed
        self.target = target
        self.score = score
        for (k, v) in kwargs.items():
            setattr(self, k, v)
            
    def __str__(self, *args, **kwargs):
        sig = "{}({})={}".format(getattr(self, "source", "*SOURCE*"),
                                 getattr(self, "seed", "*SEED*"),
                                 getattr(self, "target", "*TARGET*"))
        return "<" + str(type(self).__name__) + " " + sig + ">"
    
    def __repr__(self, *args, **kwargs):
        return self.__str__(*args, **kwargs)

WORD2VEC_DATA_DIR = '/opt/word2vec/data'
WORD2VEC_DATA_FILE = "text8-phrases.bin"

# the GoogleNews-vectors data I downloaded wasn't happy on the Mac, tended to misindex words
# e.g., model['dog'] was missing but model['og'] was found
# model = word2vec.load('/opt/word2vec/data/GoogleNews-vectors-negative300.bin')
# model = word2vec.load(os.path.join(WORD2VEC_DATA_DIR, WORD2VEC_DATA_FILE)

class SynonymGenerator(object):
    def __init__(self,
                word2vecDataDir=WORD2VEC_DATA_DIR,
                word2vecDataFile=WORD2VEC_DATA_FILE,
                wordnet=None):
        # word2vec config
        self.word2vecDataDir = word2vecDataDir
        self.word2vecDataFile = word2vecDataFile
        self.word2vecSize = 10
        self.word2vecMinimum = 0.5
        if self.word2vecDataDir and word2vecDataFile:
            self.word2vecModel = word2vec.load(os.path.join(self.word2vecDataDir, self.word2vecDataFile))
        # wordnet config    
        self.wn = wn
        self.wordnetPartsOfSpeech = True
        if self.wordnetPartsOfSpeech == True:
            self.wordnetPartsOfSpeech = ['n', 'v', 'a', 'r']
        self.wordnetlemmaMinCount = 1
        #                            POS  self/factor  up/factor    down/factor
        self.wordnetNeighborhood = (('n', (True, 1), (True, 0.5), (True, 0.5)),
                                    ('v', (True, 1), (True, 0.5), (True, 0.5)),
                                    ('a', (True, 1), (False, 0), (True, 0.5)),
                                    ('r', (True, 1), (False, 0), (True, 0.5)))
        
    def generateSynonyms(self, seed, source=True):
        if source == True:
            sources = ['word2vec', 'wordnet']
        else:
            sources = [source]
        if 'word2vec' in sources:
            for g in self.generateSynonymsWord2Vec(seed):
                yield(g)
        if 'wordnet' in sources:
            for g in self.generateSynonymsWordnet(seed):
                yield(g)
            
    def generateSynonymsWord2Vec(self, seed):
        """collocation seed must be specified as word1_word2"""
        size = self.word2vecSize
        minimum = self.word2vecMinimum
        model = self.word2vecModel
        (indexes, metrics) = model.cosine(seed, size)
        array = model.generate_response(indexes, metrics)
        for (syn, similarityScore) in array:
            if similarityScore >= minimum:
                yield(Synonym(seed=seed, target=syn, similarity=similarityScore, source='word2vec'))
                      
    def generateSynonymsWordnet(self, seed):
        """lemmas with count=0 are generally quite rare, so drop them
        may generate a lemma more than once, possible with different parameters"""
        neighborhood = self.wordnetNeighborhood
        pos = self.wordnetPartsOfSpeech
        wn = self.wn
        # Avoid lemmas with counts lower than this
        # Many WN unusual lemmas have zero
        minCount = self.wordnetlemmaMinCount
        def generateSynsetSynonyms(synset, rel, factor):
            for lemma in synset.lemmas():
                count = lemma.count()
                if count > minCount:
                    name = lemma.name()
                    if name == seed:
                        continue
                    yield(Synonym(seed=seed, target=name, lemma=lemma, synset=synset, pos=pos,factor=factor,
                                  rel=rel, count=count, score=count*factor, source='wordnet'))
    
        for pos, (here, hereFactor), (up, upFactor), (down, downFactor) in neighborhood:
            for synset in wn.synsets(seed, pos=pos):
                if here:
                    for g in generateSynsetSynonyms(synset, "self", hereFactor):
                        yield(g)
                if up:
                    for parent in synset.hypernyms():
                        for g in generateSynsetSynonyms(parent, "hypernym", upFactor):
                            yield(g)
                if down:
                    for child in synset.hyponyms():
                        for g in generateSynsetSynonyms(child, "hyponym", downFactor):
                            yield(g)


# def findSynonyms_w2v(word, size=10, minimum=0.5):
#     (indexes, metrics) = model.cosine(word, size)
#     ar = model.generate_response(indexes, metrics)
#     return [(k, v) for (k, v) in ar if v > minimum]
# 
# def findAllSynonyms_w2v(l, size=10, minimum=0.5):
#     pairs = ["{}_{}".format(w1, w2) for (w1, w2) in zip(l, l[1:])]
#     singletons = l
#     r = {}
#     for w in pairs:
#         try:
#             s = findSynonyms_w2v(w, size=size, minimum=minimum)
#             if s:
#                 r[w] = s
#         except:
#             pass
#     for w in singletons:
#         try:
#             s = findSynonyms_w2v(w, size=size, minimum=minimum)
#             if s:
#                 r[w] = s
#         except:
#             pass
#     return r
# 
# def findSynonyms_wn(word, pos=None, minCount=1):
#     "lemmas with count=0 are generally quite rare, so drop them"
#     results = {}
#     def addOne(synset, proximity):
#         for lemma in synset.lemmas():
#             count = lemma.count()
#             if count > minCount:
#                 name = lemma.name()
#                 if name == word:
#                     continue
#                 found = results.get(name)
#                 if not found or found["count"] < count:
#                     # add/update
#                     results[name] = {"name": name,
#                                      "pos": pos,
#                                      "proximity": proximity,
#                                      "count": count,
#                                      "score": count * proximity}
# 
#     for pos, (here, hereProx), (up, upProx), (down, downProx) in (('n', (True, 1), (True, 0.5), (True, 0.5)),
#                                                              ('v', (True, 1), (True, 0.5), (True, 0.5)),
#                                                              ('a', (True, 1), (False, 0), (True, 0.5)),
#                                                              ('r', (True, 1), (False, 0), (True, 0.5))):
#         for synset in wn.synsets(word, pos=pos):
#             if here:
#                 addOne(synset, hereProx)
#             if up:
#                 for parent in synset.hypernyms():
#                     addOne(parent, upProx)
#             if down:
#                 for child in synset.hyponyms():
#                     addOne(child, downProx)
#     return results
# 
# def generateSynonyms(word):
#     for (s, _) in findSynonyms_w2v([word]):
#         yield (s, "word2vec")
#     for s in findSynonyms_wn(word).keys():
#         yield (s, "wordnet")
#     
