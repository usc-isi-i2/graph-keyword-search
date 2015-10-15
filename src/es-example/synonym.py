#!/usr/bin/env python

import sys, os
import word2vec

WORD2VEC_DATA_DIR = '/opt/word2vec/data'

# the GoogleNews-vectors data I downloaded wasn't happy on the Mac, tended to misindex words
# e.g., model['dog'] was missing but model['og'] was found
# model = word2vec.load('/opt/word2vec/data/GoogleNews-vectors-negative300.bin')
model = word2vec.load(os.path.join(WORD2VEC_DATA_DIR, "text8-phrases.bin"))

def findSynonyms_w2v(word, size=10, minimum=0.5):
    (indexes,metrics) = model.cosine(word, size)
    ar = model.generate_response(indexes, metrics)
    return [(k,v) for (k,v) in ar if v>minimum]

def findAllSynonyms_w2v(l, size=10, minimum=0.5):
    pairs = ["{}_{}".format(w1,w2) for (w1,w2) in zip(l, l[1:])]
    singletons = l
    r = {}
    for w in pairs:
        try:
            s = findSynonyms_w2v(w, size=size, minimum=minimum)
            if s:
                r[w] = s
        except:
            pass
    for w in singletons:
        try:
            s = findSynonyms_w2v(w, size=size, minimum=minimum)
            if s:
                r[w] = s
        except:
            pass
    return r

from nltk.corpus import wordnet as wn

def findSynonyms_wn(word, pos=None, minCount=1):
    "lemmas with count=0 are generally quite rare"
    results = {}
    def addOne(synset, proximity):
        for lemma in synset.lemmas():
            count = lemma.count()
            if count > minCount:
                name = lemma.name()
                if name == word:
                    continue
                found = results.get(name)
                if not found or found["count"] < count:
                    # add/update
                    results[name] = {"name": name,
                                     "pos": pos,
                                     "proximity": proximity,
                                     "count": count,
                                     "score": count*proximity}

    for pos,(here,hereProx),(up,upProx),(down,downProx) in ( ('n', (True, 1), (True, 0.5), (True, 0.5) ),
                                                             ('v', (True, 1), (True, 0.5), (True, 0.5) ),
                                                             ('a', (True, 1), (False, 0), (True, 0.5) ),
                                                             ('r', (True, 1), (False, 0), (True, 0.5) )):
        for synset in wn.synsets(word, pos=pos):
            if here:
                addOne(synset, hereProx)
            if up:
                for parent in synset.hypernyms():
                    addOne(parent, upProx)
            if down:
                for child in synset.hyponyms():
                    addOne(child, downProx)
    return results

def generateSynonyms(word):
    for (s,_) in findSynonyms_w2v([word]):
        yield (s, "word2vec")
    for s in findSynonyms_wn(word).keys():
        yield (s, "wordnet")
    
