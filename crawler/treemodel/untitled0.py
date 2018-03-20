#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from gensim.models import Word2Vec
import pandas as pd
import spacy
import re
import os
import codecs
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag
import seaborn as sns

def entity_dict(df):
    e = df.dropna()
    e['word'] = e['word'].str.lower()
    edict = e.set_index('word')['entity'].to_dict()
    return edict

def merge_phrases(matcher, doc, i, matches):
    '''
    Merge a phrase. We have to be careful here because we'll change the token indices.
    To avoid problems, merge all the phrases once we're called on the last match.
    '''
    if i != len(matches)-1:
        return None
    spans = [(ent_id, label, doc[start : end]) for ent_id, label, start, end in matches]
    for ent_id, label, span in spans:
        span.merge('NNP' if label else span.root.tag_, span.text, nlp.vocab.strings[label]) 

nlp = spacy.load('en')

entity_cb = pd.read_csv('CTBC_mod5.csv',encoding = 'utf-8')
en_dict = entity_dict(entity_cb)
entity_list = list(en_dict.keys())
stop_words = set(stopwords.words('english'))

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
    
    text2 = text2.lower()
    
    matcher = spacy.matcher.Matcher(nlp.vocab)
    for key, value in en_dict.items():
        key_len = len(key.split(' '))
        if key_len == 1:
            matcher.add(entity_key=value, label=value, attrs={}, specs=[[{spacy.attrs.ORTH:key}]], on_match=merge_phrases) #merge_phrases
        else:
            specs_list = []
            for k in range(key_len):
                specs_list.append({spacy.attrs.ORTH:key.split(' ')[k]})
            matcher.add(entity_key=value, label=value, attrs={}, specs=[specs_list], on_match=merge_phrases)    

    doc = nlp(text2)
    #doc = nlp("the evolution of oil prices and the euro exchange rate points to lower inflation than the conditioning assumptions underlying the ecb staff¡šs most recent published forecasts.")
    
    try:
        matcher(doc)
    except:
        print(doc,'is unavalable.')
        continue
    
    for sent in doc.sents:
        for word in sent:
            if word not in stop_words:
                if (word.pos_ != 'RB') & (word.pos_ != 'CD') & (word.pos_ !='CC'):
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


