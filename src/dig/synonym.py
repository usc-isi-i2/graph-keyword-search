#!/usr/bin/env python

import sys, os

from nltk.corpus import wordnet as wn
import word2vec
import urllib
from urllib.parse import quote
from builtins import setattr

class Synonym(object):

    """Synonym records a link between two surface forms:
a known word or collocation (the seed or indicator)
e.g., 'blue', 'eye_color' 
and 
a word or collocation believed to be equivalent/or related (the target or content)
e.g., 'sky'."""

    def __init__(self, *args, indicator=None, content=None, score=1.0, source=None, **kwargs):
        self.indicator = indicator
        self.content = content
        self.score = score
        self.source = source
        for (k, v) in kwargs.items():
            setattr(self, k, v)
            
    def __str__(self, *args, **kwargs):
        sig = "{}({})=>{}{}".format(getattr(self, "source", "*SOURCE*"),
                                    getattr(self, "indicator", "*INDICATOR*"),
                                    getattr(self, "content", "*CONTENT*"),
                                    "" if getattr(self, "score", 1.0)==1.0 else getattr(self, "score", "unknown"))
        return "<" + str(type(self).__name__) + " " + sig + ">"
    
    def __repr__(self, *args, **kwargs):
        return self.__str__(*args, **kwargs)

    def explain(self):
        return str(self)

# the GoogleNews-vectors data I downloaded wasn't happy on the Mac, tended to misindex words
# e.g., model['dog'] was missing but model['og'] was found
# model = word2vec.load('/opt/word2vec/data/GoogleNews-vectors-negative300.bin')
# model = word2vec.load(os.path.join(WORD2VEC_DATA_DIR, WORD2VEC_DATA_FILE)

class SynonymGenerator(object):
    pass

WORD2VEC_DATA_DIR = '/opt/word2vec/data'
WORD2VEC_DATA_FILE = "text8-phrases.bin"
WORD2VEC_SIZE = 10
WORD2VEC_MINIMUM_SCORE = 0.5

class Word2VecSynonymGenerator(SynonymGenerator):

    def __init__(self,
                 dataDir=WORD2VEC_DATA_DIR,
                 dataFile=WORD2VEC_DATA_FILE,
                 size=WORD2VEC_SIZE,
                 minimumScore=WORD2VEC_MINIMUM_SCORE):
        super(Word2VecSynonymGenerator, self).__init__()
        # word2vec config
        self.dataDir = dataDir
        self.dataFile = dataFile
        self.size = size
        self.minimumScore = minimumScore
        if self.dataDir and self.dataFile:
            self.word2vecModel = word2vec.load(os.path.join(self.dataDir, self.dataFile))

    def generateSynonyms(self, indicator):
        """collocation indicator must be specified as word1_word2"""
        if isinstance(indicator, (list, tuple)):
            indicator = "_".join(indicator)
        size = self.size
        minimumScore = self.minimumScore
        try:
            model = self.word2vecModel
            (indexes, metrics) = model.cosine(indicator, size)
            array = model.generate_response(indexes, metrics)
            for (syn, similarityScore) in array:
                if similarityScore >= minimum:
                    yield(Synonym(indicator=indicator, content=syn, score=similarityScore, source='word2vec'))
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


# TODO: interrogate pertanyms and derivationally_related_forms, which are stored only on the resultant lemmas
# TODO: holonyms (synechdoche), metonymy in general

class WordnetSynonymGenerator(SynonymGenerator):

    def __init__(self,
                 partsOfSpeech=WORDNET_PARTS_OF_SPEECH,
                 lemmaMinCount=WORDNET_LEMMA_MIN_COUNT,
                 neighborhood=WORDNET_NEIGHBORHOOD):
        super(WordnetSynonymGenerator, self).__init__()
        # wordnet config    
        self.wn = wn
        self.wordnetPartsOfSpeech = WORDNET_PARTS_OF_SPEECH
        self.wordnetLemmaMinCount = WORDNET_LEMMA_MIN_COUNT
        self.wordnetNeighborhood = WORDNET_NEIGHBORHOOD

    def generateSynonyms(self, indicator):
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
                    if name == indicator:
                        continue
                    yield(Synonym(indicator=indicator, content=name, lemma=lemma, synset=synset, pos=pos, factor=factor,
                                  rel=rel, count=count, score=count*factor, source='wordnet'))
    
        for pos, (here, hereFactor), (up, upFactor), (down, downFactor) in neighborhood:
            for synset in wn.synsets(indicator, pos=pos):
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

    def generateSynonyms(self, indicator):
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

    def generateSynonyms(self, indicator):
        pass

class Thesaurus(object):
    def __init__(self,
                 word2vec_enable=True,
                 word2vec_data_dir=WORD2VEC_DATA_DIR,
                 word2vec_data_file=WORD2VEC_DATA_FILE,
                 word2vec_size=WORD2VEC_SIZE,
                 word2vec_minimum_score=WORD2VEC_MINIMUM_SCORE,
                 wordnet_enable=True,
                 # wordnetPartsOfSpeech=WORDNET_PARTS_OF_SPEECH,
                 wordnet_lemma_min_count=WORDNET_LEMMA_MIN_COUNT,
                 # wordnet_neighborhood=WORDNET_NEIGHBORHOOD,
                 wordnet_n_enable = True,
                 wordnet_n_self_factor = 1.0,
                 wordnet_n_hypernym_factor = 0.5,
                 wordnet_n_hyponym_factor = 0.5,
                 wordnet_v_enable = True,
                 wordnet_v_self_factor = 1.0,
                 wordnet_v_hypernym_factor = 0.5,
                 wordnet_v_hyponym_factor = 0.5,
                 wordnet_a_enable = True,
                 wordnet_a_self_factor = 1.0,
                 wordnet_a_hypernym_factor = 0,
                 wordnet_a_hyponym_factor = 0.5,
                 wordnet_r_enable = True,
                 wordnet_r_self_factor = 1.0,
                 wordnet_r_hypernym_factor = 0,
                 wordnet_r_hyponym_factor = 0.5,
                 swoogle_enable=False,
                 swoogle_uri_template=None,
                 easyesa_enable=False,
                 **kwargs):
        synonymGenerators = {}
        if word2vec_enable:
            synonymGenerators['word2vec'] = Word2VecSynonymGenerator(dataDir=word2vec_data_dir,
                                                                     dataFile=word2vec_data_file,
                                                                     size=word2vec_size,
                                                                     minimumScore=word2vec_minimum_score)
        if wordnet_enable:
            partsOfSpeech = []
            neighborhood = []
            if wordnet_n_enable:
                partsOfSpeech.append('n')
                neighborhood.append( ('n', 
                                      (wordnet_n_self_factor>0, wordnet_n_self_factor), 
                                      (wordnet_n_hypernym_factor>0, wordnet_n_hypernym_factor), 
                                      (wordnet_n_hyponym_factor>0, wordnet_n_hyponym_factor)) )
            if wordnet_v_enable:
                partsOfSpeech.append('v')
                neighborhood.append( ('v', 
                                      (wordnet_v_self_factor>0, wordnet_v_self_factor), 
                                      (wordnet_v_hypernym_factor>0, wordnet_v_hypernym_factor), 
                                      (wordnet_v_hyponym_factor>0, wordnet_v_hyponym_factor)) )
            if wordnet_a_enable:
                partsOfSpeech.append('a')
                neighborhood.append( ('a', 
                                      (wordnet_a_self_factor>0, wordnet_a_self_factor), 
                                      (wordnet_a_hypernym_factor>0, wordnet_a_hypernym_factor), 
                                      (wordnet_a_hyponym_factor>0, wordnet_a_hyponym_factor)) )
            if wordnet_r_enable:
                partsOfSpeech.append('r')
                neighborhood.append( ('r', 
                                      (wordnet_r_self_factor>0, wordnet_r_self_factor), 
                                      (wordnet_r_hypernym_factor>0, wordnet_r_hypernym_factor), 
                                      (wordnet_r_hyponym_factor>0, wordnet_r_hyponym_factor)) )
            synonymGenerators['wordnet'] = WordnetSynonymGenerator(partsOfSpeech=partsOfSpeech,
                                                                   lemmaMinCount=wordnet_lemma_min_count,
                                                                   neighborhood=neighborhood)
        if swoogle_enable:
            synonymGenerators['swoogle'] = SwoogleSynonymGenerator(uriTemplate=swoogle_uri_template)
        if easyesa_enable:
            synonymGenerators['easyESA'] = EasyESASynonymGenerator()
        self.synonymGenerators = synonymGenerators
        
    def generateSynonyms(self, indicator):
        for (_, syngen) in self.synonymGenerators.items():
            for g in syngen.generateSynonyms(indicator):
                yield(g)
