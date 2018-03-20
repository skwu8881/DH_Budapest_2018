# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 20:41:43 2018

@author: fishtoby
"""

import jieba
import sys

from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfVectorizer

corpus = []
with open('algorithms/in.txt', 'r') as f:
    for line in f:
        corpus.append(" ".join(jieba.cut(line.split(',')[0], cut_all=True)))

vectorizer = TfidfVectorizer()
tfidf = vectorizer.fit_transform(corpus)
print(tfidf.shape)

open('algorithms/in2.txt','w').close()
words = vectorizer.get_feature_names()
for i in range(len(corpus)):
    for j in range(len(words)):
        if tfidf[i,j] > 1e-5:
            with open('algorithms/in2.txt','a') as nowF:
              nowF.write(str(words[j]))
              nowF.write(' ')
              nowF.write(str(tfidf[i,j]))
              nowF.write('\n')
