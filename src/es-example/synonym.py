#!/usr/bin/python3

import sys, os
import word2vec

WORD2VEC_DATA_DIR = '/opt/word2vec/data'

# the GoogleNews-vectors data I downloaded wasn't happy on the Mac, tended to misindex words
# e.g., model['dog'] was missing but model['og'] was found
# model = word2vec.load('/opt/word2vec/data/GoogleNews-vectors-negative300.bin')
model = word2vec.load(os.path.join(WORD2VEC_DATA_DIR, "text8.bin"))

indexes, metrics = model.cosine('socks')

