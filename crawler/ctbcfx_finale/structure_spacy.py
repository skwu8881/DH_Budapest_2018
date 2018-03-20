#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import nltk
import spacy
import codecs
import pandas as pd
from nltk import Tree
from nltk.util import ngrams
from collections import OrderedDict
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize

def entity_dict(df):
    # transfer dataframe to dictionary
    e = df.dropna()
    e['word'] = e['word'].str.lower()
    edict = e.set_index('word')['entity'].to_dict()
    return edict
    
def get_ngrams(text, n):
    n_grams = ngrams(word_tokenize(text), n)
    phrase = [' '.join(grams) for grams in n_grams]
    return phrase

def sentence_tokenize(article):
    # transfer article into sentence list
    sent_tokenize_list = sent_tokenize(article)
    sent_list = [x.lower() for x in sent_tokenize_list]
    return sent_list

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
    
def tok_format(tok):
    # return word_entity
    return "_".join([tok.orth_,tok.ent_type_]) 
    
def to_nltk_tree(node):
    # nltk_tree
    if node.n_lefts + node.n_rights > 0:
        return Tree(tok_format(node), [to_nltk_tree(child) for child in node.children])
    else:
        return tok_format(node)

def traverseTree(tree):
    # dfs algorithm
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

def generate_text_list(file_path):
    # find all txt file in path
    txt_list = []
    for root, dirs, files in os.walk(file_path):
        for file in files:
            if '.txt' in file:
                txt_list.append(os.path.join(root, file))
    return txt_list

def read_text_file(txt):
    # three encoding read file
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
        
    rfile.close()
    return text2

def create_save_file(save_path,txt):
    save_file = os.path.join(save_path,txt.split('/')[-1])
    wfile = codecs.open(save_file,'w','utf-8') 
    return wfile

def market_recognize(market_dict,market_pin,sent):
    # given sentence , indentify market
    for key,value in market_dict.items():
        if len(key) < 5:
            match = re.search('\s%s\s' %key,sent)
            if match != None:
                if value not in market_pin:
                    market_pin +='/'+value
        else:
            if key in sent:
                market_pin = value
    return market_pin

def remove_overlap(en_dict,entity_list,sent):
    # remove entity overlap , due to spacy issue 
    big_list =[]
    remove_list =[]
    en_sent_dict = en_dict.copy()
    for i in range(2,5):
         temp = get_ngrams(sent,i)
         for phrase in temp:
             if phrase in entity_list:
                 big_list.append(phrase)
    
    uni_gram = get_ngrams(sent,1)
    for word in uni_gram:
        for phrase in big_list:
            if word in phrase:
                remove_list.append(word)
    
    for removal in remove_list:
        if removal in entity_list:
            try:
                en_sent_dict.pop(removal)  
            except:
                pass
    return en_sent_dict

def negation_type(sent):
    # use typed dependency to remove negation sentence
    negterm = ["n't",'no','not','never','none','nothing','nobody','noone','nowhere','without','hardly',
           'barely','rarely','seldom','against','minus']
    neg_dep_list = ['det','prt','advmmod','dobj','nsubj','dep']
    
    rot = [w for w in sent if w.head is w][0] #root
    td_list = []
    neg_type1 = False
    for wordss in sent:
        # get typed dependency 
        typed_d = ''.join([str(wordss.dep_),'(',str(wordss.head),',',str(wordss),')'])
        Td = typed_d.split('(')[0]
        gov = typed_d.split('(')[1].split(',')[0]
        dep = typed_d.split(',')[1].split(')')[0]
        td_list.append(''.join([str(wordss.dep_),'(',str(wordss.head),',',str(wordss),')']))
        
        # negation reconigze
        if (Td == 'neg') & (gov in entity_list):
            neg_type1 = True

        if (Td in neg_dep_list) & (dep in negterm) & (gov in entity_list):
            neg_type1 = True

        if (Td == 'neg') & (gov == str(rot)) & (rot.pos_ == 'VERB'):
            neg_type1 = True

        if (Td in neg_dep_list) & (dep in negterm) &(gov == str(rot)) & (rot.pos_ == 'VERB'):
            neg_type1 = True
    
    return neg_type1
    
def create_matcher(en_sent_dict):
    # NER matcher 
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
    return matcher
    
def entity_sentiment_index(dfs_list):
    # get index of entity & sentence 
    for word in dfs_list:
        indice = [j for j,x in enumerate(dfs_list) if '##' in x]
        indice_sent = [j for j,x in enumerate(dfs_list) if '@#' in x]
        
    length = len(sent) / 5 + 1
    # distance between keyword & sentiment
    for i in range(len(indice_sent)):
        ta = [abs(x-indice_sent[i]) for x in indice if abs(x-indice_sent[i] <= length)]
        try:
            min(ta)
        except:
            continue
        for z in indice:
            if indice_sent[i] - min(ta) <= z <= indice_sent[i]+min(ta):
                en_index = z
                sen_index = indice_sent[i]
                
    return (en_index,sen_index)

def entity_sentiment_pair(dfs_list,en_index,sen_index):
    word = str(dfs_list[en_index].split('_')[0])
    sen_word = str(dfs_list[sen_index].split('_')[0])
    sen_type = str(dfs_list[sen_index].split('_')[1])
    return (word,sen_word,sen_type)

if __name__ == '__main__':
    # load spacy model
    nlp = spacy.load('en')
    
    # load entity csv
    entity_cb = pd.read_csv('/Users/xiechangrun/Desktop/sentiment1103.csv',encoding = 'utf-8')
    en_dict = entity_dict(entity_cb)
    entity_list = list(en_dict.keys())
    
    # load market csv
    market_path = pd.read_csv('/Users/xiechangrun/Desktop/ctbcfx/treemodel/market.csv',encoding = 'utf-8')
    market_path['entity'] = market_path['entity'].astype(str).str.replace('central#','')
    market_dict = entity_dict(market_path)
    
    # report path & save path
    file_path = '/Users/xiechangrun/Desktop/new201710'    
    save_path = '/Users/xiechangrun/Desktop/pycsv_files/new_test'
    
    eas_list = []
    count = 0
    txt_list = generate_text_list(file_path)
    #each txt file
    for txt in txt_list: 
        text_detail = read_text_file(txt)
        save_file = create_save_file(save_path,txt)
        sent_list = sentence_tokenize(text_detail)
        market_pin = ''
        # each sentence
        for each in sent_list: 
            market_pin = market_recognize(market_dict,market_pin,each)
            en_sent_dict = remove_overlap(en_dict,entity_list,each)
            # named entity reconigtion
            matcher = create_matcher(en_sent_dict)
            doc = nlp(each)
            
            try:
                matcher(doc)
            except:
                print(doc,'is unavalable.')
                continue
            
            dfs_list = []
            # get typed dependency
            for sent in doc.sents:
                neg_type1 = negation_type(sent)
                traverseTree(to_nltk_tree(sent.root))
                en_index,sen_index = entity_sentiment_index(dfs_list)
                word,sen_word,sen_type = entity_sentiment_pair(dfs_list,en_index,sen_index)
                if neg_type1 == False:
                    info_dict = OrderedDict()
                    info_dict['article'] = count
                    info_dict['day'] = count//10 + 1
                    info_dict['word'] = word
                    info_dict['sen_word'] = sen_word
                    info_dict['sen_type'] = sen_type.split('@#')[1]
                    info_dict['market'] = market_pin
                    info_dict['sentiment'] = str(sent)
                    #info_dict['date'] = pd.to_datetime('2017-07-12')
                    eas_list.append(info_dict)
        count += 1
        
    eas_frame = pd.DataFrame(eas_list)
    eas_frame['len_sent'] = eas_frame['sentiment'].apply(lambda x:len(x))
    eas_frame.to_csv('sentiment_result.csv',encoding = 'utf-8',index=None)
