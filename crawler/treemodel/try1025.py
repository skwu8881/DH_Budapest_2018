#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import spacy
import pandas as pd
from nltk import Tree
import nltk
from nltk.tokenize import sent_tokenize
import os
from nltk.util import ngrams
from nltk.tokenize import word_tokenize
import codecs
from datetime import datetime
import re
from collections import OrderedDict

def get_ngrams(text, n):
    n_grams = ngrams(word_tokenize(text), n)
    phrase = [' '.join(grams) for grams in n_grams]
    return phrase

def sentence_tokenize(article):
    sent_tokenize_list = sent_tokenize(article)
    sent_list = [x.lower() for x in sent_tokenize_list]
    return sent_list

def entity_dict(df):
    # entity dataframe to dictionary
    e = df.dropna()
    e['word'] = e['word'].str.lower()
    edict = e.set_index('word')['entity'].to_dict()
    return edict

def merge_phrases(matcher, doc, i, matches):
    # custom named entity
    '''
    Merge a phrase. We have to be careful here because we'll change the token indices.
    To avoid problems, merge all the phrases once we're called on the last match.
    '''
    if i != len(matches)-1:
        return None
    spans = [(ent_id, label, doc[start : end]) for ent_id, label, start, end in matches]
    for ent_id, label, span in spans:
        span.merge('NNP' if label else span.root.tag_, span.text, nlp.vocab.strings[label]) 
    
def tok_format(tok):
    return "_".join([tok.orth_,tok.ent_type_]) # tok.lemma_, 
    
def to_nltk_tree(node):
    # get nltk tree
    if node.n_lefts + node.n_rights > 0:
        return Tree(tok_format(node), [to_nltk_tree(child) for child in node.children])
    else:
        return tok_format(node)

def traverseTree(tree):
    # get dependency tree
    global dfs_list
    if type(tree) == nltk.tree.Tree:
        dfs_list.append(tree.label())
    else:
        dfs_list.append(tree)
        #print("tree:", tree)
    for subtree in tree:
        if type(subtree) == nltk.tree.Tree:
            traverseTree(subtree)
        else:
            dfs_list.append(subtree)  
    
now = datetime.now()
# load spacy model
nlp = spacy.load('en')

# load entity & sentiment dictionary
entity_cb = pd.read_csv('/Users/xiechangrun/Desktop/ctbc1025.csv',encoding = 'utf-8')
en_dict = entity_dict(entity_cb)

# load market dictionary (for classification)
market_path = pd.read_csv('market.csv',encoding = 'utf-8')
market_path['entity'] = market_path['entity'].astype(str).str.replace('central#','')
market_dict = entity_dict(market_path)

#fomc_news = pd.read_csv('zeroht0319.csv',encoding = 'utf-8')
fomc_news = pd.read_csv('/Users/xiechangrun/Desktop/zdata2015.csv',encoding = 'utf-8')
fomc_news = fomc_news[(pd.to_datetime(fomc_news.time) >= pd.to_datetime('2015-01-31')) & (pd.to_datetime(fomc_news.time) <= pd.to_datetime('2015-08-01'))]
print(len(fomc_news))


count_list = []
eas_list = []
ea_list = []
ea_market = []
market_list = []

#nothing_list = ['as well as','as well','zero lower bound']
negterm = ["n't",'no','not','never','none','nothing','nobody','noone','nowhere','without','hardly',
           'barely','rarely','seldom','against','minus']
#negaux = ['should','could','would','might','ought']
neg_dep_list = ['det','prt','advmmod','dobj','nsubj','dep']

entity_match_dict = {'commodity':['good','bad'],'econ':['good','bad'],'rate':['up','down'],'inflation':['up','down']
                    ,'labor':['good','bad'],'employ':['good','bad','up','down'],'equity':['good','bad'],'treasury':['good','bad']
                    ,'yeild':['up','down']}

#root2 = "fomc"            
             
count = 0
for each in fomc_news['content']:
    warning_staff = []
    market_pin = ''
    eas_count={}
    ea_count={}
    '''
    name = str(fomc_news['time'][count])+str(count)+'.txt'
    save_file = os.path.join(root2,name)
    
    # 開檔與寫入標題時間
    wfile = codecs.open(save_file,'w','utf-8')
    wfile.write(str(fomc_news['title'][count])+ '\n')
    wfile.write(str(fomc_news['time'][count])+ '\n')
    wfile.write(each+ '\n')
    '''                                  
    subsent_list = []
    # nltk斷句
    sent_list = sent_tokenize(each)
    
    # 更詳細的斷句
    for sent in sent_list:
        for subsent in sent.split(','):
            if len(subsent.split(' ')) > 1: #3
                for smaller_sent in subsent.split(':'): 
                    subsent_list.append(smaller_sent)


    entity_list = list(en_dict.keys())
    
    for each in subsent_list:
        big_list = []
        remove_list = []
        en_sent_dict = en_dict.copy()
        
        if 'warning' in each:
            warning_staff.append(each)
        
        if ' if ' in each: #去除假設性語句
            continue
        
        # market recognize
        for key,value in market_dict.items():
            if len(key) < 5:
                match = re.search('\s%s\s' %key,each)
                if match != None:
                    market_pin = value
            else:
                if key in each:
                    market_pin = value
        market_list.append(market_pin)
        
        # remove overlap
        for i in range(2,5):
             temp = get_ngrams(each,i)
             for phrase in temp:
                 if phrase in entity_list:
                     big_list.append(phrase)
        
        uni_gram = get_ngrams(each,1)
        for word in uni_gram:
            for phrase in big_list:
                if word in phrase:
                    remove_list.append(word)
        
        for removal in remove_list:
            if removal in entity_list:
                try:
                    en_sent_dict.pop(removal)  
                except:
                    #print('check whether',removal,'is removed.')
                    continue
        
        #named entity recongition
        try:
            matcher = spacy.matcher.Matcher(nlp.vocab)
            for key, value in en_sent_dict.items():
                key_len = len(key.split(' '))
                if key_len == 1:
                    matcher.add(entity_key=value, label=value, attrs={}, specs=[[{spacy.attrs.ORTH:key}]], on_match=merge_phrases) #merge_phrases
                else:
                    specs_list = []
                    for k in range(key_len):
                        specs_list.append({spacy.attrs.ORTH:key.split(' ')[k]})
                    matcher.add(entity_key=value, label=value, attrs={}, specs=[specs_list], on_match=merge_phrases)    
        
        except:
            continue

        doc = nlp(each)
        try:
            matcher(doc)
        except:
            #print(each,'is unavalible.')
            continue
        
        dfs_list = []   
        for sent in doc.sents:
            #sent = nlp('interesting hedgeing against the chance of a "no rate hike" was "aggressive" today in fed funds futures.')
            
            rot = [w for w in sent if w.head is w][0] #root
            gg_list = []
            neg_type1 = False
            # get typed dependency
            for wordss in sent:
                typed_d = ''.join([str(wordss.dep_),'(',str(wordss.head),',',str(wordss),')'])
                Td = typed_d.split('(')[0]
                gov = typed_d.split('(')[1].split(',')[0]
                dep = typed_d.split(',')[1].split(')')[0]
                
                # negation rules
                if (Td == 'neg') & (gov in entity_list):
                    neg_type1 = True

                if (Td in neg_dep_list) & (dep in negterm) & (gov in entity_list):
                    neg_type1 = True

                if (Td == 'neg') & (gov == str(rot)) & (rot.pos_ == 'VERB'):
                    neg_type1 = True

                if (Td in neg_dep_list) & (dep in negterm) &(gov == str(rot)) & (rot.pos_ == 'VERB'):
                    neg_type1 = True
                    
                gg_list.append(typed_d)  
                
            dfs_list = []
            
            #to_nltk_tree(sent.root).pretty_print()
            
            # build dependency tree
            traverseTree(to_nltk_tree(sent.root))
            #nltk_tree_list.append(to_tp_tree(sent.root))
            
            # get index of entity & sentiment
            for word in dfs_list:
                indice = [j for j,x in enumerate(dfs_list) if '##keyword' in x] #entity-aspect signal 
                #indice_sent = [j for j,x in enumerate(dfs_list) if '@#' in x] #sentiment signal
                
            if len(indice) > 3:
                if neg_type1 == True:
                    print(str(sent))
                if neg_type1 == False:
                    print(str(sent))