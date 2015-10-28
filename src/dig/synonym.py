#!/usr/bin/env python

import sys, os

from nltk.corpus import wordnet as wn
import word2vec
import urllib
from urllib.parse import quote
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

    @property
    def indicator(self):
        return ["indicator", self.seed]

    @property
    def content(self):
        return self.target

# the GoogleNews-vectors data I downloaded wasn't happy on the Mac, tended to misindex words
# e.g., model['dog'] was missing but model['og'] was found
# model = word2vec.load('/opt/word2vec/data/GoogleNews-vectors-negative300.bin')
# model = word2vec.load(os.path.join(WORD2VEC_DATA_DIR, WORD2VEC_DATA_FILE)

class SynonymGenerator(object):
    pass

WORD2VEC_DATA_DIR = '/opt/word2vec/data'
WORD2VEC_DATA_FILE = "text8-phrases.bin"
WORD2VEC_SIZE = 10
WORD2VEC_MINIMUM = 0.5

class Word2VecSynonymGenerator(SynonymGenerator):

    def __init__(self,
                 word2vecDataDir=WORD2VEC_DATA_DIR,
                 word2vecDataFile=WORD2VEC_DATA_FILE,
                 word2vecSize=WORD2VEC_SIZE,
                 word2vecMinimum=WORD2VEC_MINIMUM):
        super(Word2VecSynonymGenerator, self).__init__()
        # word2vec config
        self.word2vecDataDir = word2vecDataDir
        self.word2vecDataFile = word2vecDataFile
        self.word2vecSize = word2vecSize
        self.word2vecMinimum = word2vecMinimum
        if self.word2vecDataDir and self.word2vecDataFile:
            self.word2vecModel = word2vec.load(os.path.join(self.word2vecDataDir, self.word2vecDataFile))

    def generateSynonyms(self, seed):
        """collocation seed must be specified as word1_word2"""
        if isinstance(seed, (list, tuple)):
            seed = "_".join(seed)
        size = self.word2vecSize
        minimum = self.word2vecMinimum
        try:
            model = self.word2vecModel
            (indexes, metrics) = model.cosine(seed, size)
            array = model.generate_response(indexes, metrics)
            for (syn, similarityScore) in array:
                if similarityScore >= minimum:
                    yield(Synonym(seed=seed, target=syn, similarity=similarityScore, source='word2vec'))
        except:
            pass
    pass

WORDNET_PARTS_OF_SPEECH = ['n', 'v', 'a', 'r']
WORDNET_LEMMA_MIN_COUNT = 1
#                       POS  self/factor  up/factor   down/factor
WORDNET_NEIGHBORHOOD = (('n', (True, 1), (True, 0.5), (True, 0.5)),
                        ('v', (True, 1), (True, 0.5), (True, 0.5)),
                        ('a', (True, 1), (False, 0),  (True, 0.5)),
                        ('r', (True, 1), (False, 0),  (True, 0.5)))


class WordnetSynonymGenerator(SynonymGenerator):

    def __init__(self,
                 wordnetPartsOfSpeech=WORDNET_PARTS_OF_SPEECH,
                 wordnetLemmaMinCount=WORDNET_LEMMA_MIN_COUNT,
                 wordnetNeighborhood=WORDNET_NEIGHBORHOOD):
        super(WordnetSynonymGenerator, self).__init__()
        # wordnet config    
        self.wn = wn
        self.wordnetPartsOfSpeech = WORDNET_PARTS_OF_SPEECH
        self.wordnetLemmaMinCount = WORDNET_LEMMA_MIN_COUNT
        self.wordnetNeighborhood = WORDNET_NEIGHBORHOOD

    def generateSynonyms(self, seed):
        """lemmas with count=0 are generally quite rare, so drop them
        may generate a lemma more than once, possible with different parameters"""
        neighborhood = self.wordnetNeighborhood
        pos = self.wordnetPartsOfSpeech
        wn = self.wn
        # Avoid lemmas with counts lower than this
        # Many WN unusual lemmas have zero
        minCount = self.wordnetLemmaMinCount
        def generateSynsetSynonyms(synset, rel, factor):
            for lemma in synset.lemmas():
                count = lemma.count()
                if count > minCount:
                    name = lemma.name()
                    if name == seed:
                        continue
                    yield(Synonym(seed=seed, target=name, lemma=lemma, synset=synset, pos=pos, factor=factor,
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


class SwoogleSynonymGenerator(SynonymGenerator):

    def __init(self):
        super(SwoogleSynonymGenerator, self).__init__()
        # swoogle config
        self.swoogle = True
        self.swoogleUriTemplate = '''http://swoogle.umbc.edu/StsService/GetStsSim?operation=api&phrase1="{}"&phrase2="{}"'''

    def generateSynonyms(self, seed):
        """Incomplete"""
        score = 0
        url = self.swoogleUriTemplate.format(quote)
        try:
            request = urllib.request.Request(url)
            response = urllib.request.urlopen(request)
            score = str(response.read().decode('utf-8')).replace('\"','')
            score = float(score)
        except Exception as _:
            pass
        pass

class EasyESASynonymGenerator(SynonymGenerator):
    def __init(self):
        super(EasyESASynonymGenerator, self).__init__()

    def generateSynonyms(self, seed):
        pass

class Thesaurus(object):
    def __init__(self,
                 word2vec=True,
                 word2vecDataDir=WORD2VEC_DATA_DIR,
                 word2vecDataFile=WORD2VEC_DATA_FILE,
                 word2vecSize=WORD2VEC_SIZE,
                 word2vecMinimum=WORD2VEC_MINIMUM,
                 wordnet=True,
                 wordnetPartsOfSpeech=WORDNET_PARTS_OF_SPEECH,
                 wordnetLemmaMinCount=WORDNET_LEMMA_MIN_COUNT,
                 wordnetNeighborhood=WORDNET_NEIGHBORHOOD,
                 swoogle=False,
                 easyESA=False,
                 **kwargs):
        synonymGenerators = {}
        if word2vec:
            synonymGenerators['word2vec'] = Word2VecSynonymGenerator(word2vecDataDir=word2vecDataDir,
                                                                     word2vecDataFile=word2vecDataFile,
                                                                     word2vecSize=word2vecSize,
                                                                     word2vecMinimum=word2vecMinimum)
        if wordnet:
            synonymGenerators['wordnet'] = WordnetSynonymGenerator(wordnetPartsOfSpeech=wordnetPartsOfSpeech,
                                                                   wordnetLemmaMinCount=wordnetLemmaMinCount,
                                                                   wordnetNeighborhood=wordnetNeighborhood)
        if swoogle:
            synonymGenerators['swoogle'] = SwoogleSynonymGenerator()
        if easyESA:
            synonymGenerators['easyESA'] = EasyESASynonymGenerator()
        self.synonymGenerators = synonymGenerators
        
    def generateSynonyms(self, seed):
        for (_, syngen) in self.synonymGenerators.items():
            for g in syngen.generateSynonyms(seed):
                yield(g)
