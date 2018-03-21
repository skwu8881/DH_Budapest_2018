#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from gensim.models import Word2Vec
import pandas as pd
import logging
import re
import os
import codecs
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag
import seaborn as sns

txt_list = []
for root, dirs, files in os.walk("/Users/xiechangrun/Desktop/new201710"):
    for file in files:
        if '.txt' in file:
            txt_list.append(os.path.join(root, file))

output_name='/Users/xiechangrun/Desktop/new_central/w400-5-5-model'
trainData= []
for txt in txt_list:
    sentence = []
    try:
        rfile = codecs.open(txt, "r", "big5")
        text2 = ''.join(x for x in rfile.readlines())
   
    except:
        try:
            rfile = codecs.open(txt, "r", "utf-8")
            text2 = ''.join(x for x in rfile.readlines())
        except:
            rfile = codecs.open(txt, "r", "Latin1")
            text2 = ''.join(x for x in rfile.readlines())

    stop_words = set(stopwords.words('english'))

    words = word_tokenize(text2)
    tagged = pos_tag(words)
    n = 0
    for word in words:
        word = re.sub(r'[^\w]', '',word).lower()
        pos = tagged[n][1] 
        n+= 1
        if word not in stop_words:
            if (pos != 'RB') & (pos != 'CD') & (pos !='CC'):
                sentence.append(word)
            
    trainData.append(sentence)

model = Word2Vec(trainData, size=200, window=5, min_count=3, workers=4)
     
# trim unneeded model memory = use (much) less RAM
model.init_sims(replace=True)

model.save(output_name) 

model1=Word2Vec.load('/Users/xiechangrun/Desktop/new_central/w400-5-5-model')

word_sim = model1.most_similar(['rate'],topn = 30)
df = pd.DataFrame(word_sim,columns = ['word','sim'])
sns.barplot(x = 'sim',data = df,y = 'word',color = 'blue')


'''
sim_list = []
for each in range(len(word_sim)):
    sim_list.append(word_sim[each][0])
    tagged = pos_tag(sim_list)
    for element in tagged:
        if element[1] == '':
            
'''
