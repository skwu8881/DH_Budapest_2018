# -*- coding: utf-8 -*-
import numpy as np
import spacy
import pandas as pd
from nltk import Tree
import nltk
from nltk.tokenize import sent_tokenize
from nltk.util import ngrams
from nltk.tokenize import word_tokenize
from datetime import datetime
import pickle
from collections import OrderedDict
from lib.ctbcfxSQL import ctbcfxSQL

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
entity_cb = pd.read_csv(r'C:\Users\z00013855\Desktop\treemodel\ctbc1026.csv',encoding = 'utf-8') #CTBC_mod5
en_dict = entity_dict(entity_cb)

negterm = ["n't",'no','not','never','none','nothing','nobody','noone','nowhere','without','hardly',
               'barely','rarely','seldom','against','minus']
#negaux = ['should','could','would','might','ought']
neg_dep_list = ['det','prt','advmmod','dobj','nsubj','dep']

DBconn = ctbcfxSQL()
# preprocess of news data
with open(r'C:\Users\z00013855\Desktop\JU_try\start.txt', "rb") as fp:   # Unpickling
    start = pickle.load(fp)
    
with open(r'C:\Users\z00013855\Desktop\JU_try\end.txt', "rb") as fs:   # Unpickling
    end = pickle.load(fs)

raw_data = DBconn.query(cols='*',table='zerohedge',condition_str='(time > "2013-01-14 00:00:00") and (time < "2017-06-26 00:00:00")') #time >= "start_time" and (time < end_time)
fomc_news = pd.DataFrame(raw_data)
fomc_news['content'] = fomc_news['content'].apply(lambda x: x.lower())
'''
fomc_news['jpy_word']= fomc_news['content'].apply(lambda x:1 if 'jpy' in x else 0)
fomc_news = fomc_news.query(jpy_word>0)
'''
info_list = []
info_list2 = []

count = 0
for index in range(len(start)): 
    sen_dict = {}
    word_dict ={}
    
    start_time = pd.to_datetime(start[index])
    end_time = pd.to_datetime(end[index])
    
    limit_news = fomc_news[(fomc_news.time > start_time) & (fomc_news.time < end_time)]

    for each in limit_news['content']:
        temp_list = []       
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
                    indice = [j for j,x in enumerate(dfs_list) if '##' in x] #entity-aspect signal 
                    indice_sent = [j for j,x in enumerate(dfs_list) if '@#' in x] #sentiment signal
                
                length = len(sent) / 5 + 1
                # calculate distance between entity &sentiment
                k = 0
                m = 0
                for i in range(len(indice_sent)):
                    ta = [abs(x-indice_sent[i]) for x in indice if abs(x-indice_sent[i] <= length)]
                    try:
                        min(ta)
                    except:
                        continue
                    for z in indice:
                        if indice_sent[i] - min(ta) <= z <= indice_sent[i]+min(ta):
                            a_index = z
                            b_index = indice_sent[i]
                            word = str(dfs_list[a_index].split('_')[0])
                            EA = str(dfs_list[a_index].split('_')[1].split('##')[1])
                            sen_word = str(dfs_list[b_index].split('_')[0])
                            sen_type = str(dfs_list[b_index].split('_')[1].split('@#')[1])
                            
                            #info_dict = OrderedDict()
                            if (m == 0):
                                m+=1
                            if neg_type1 == False:
                                if sen_word in sen_dict.keys():
                                    sen_dict['%s' %sen_word] += 1
                                    sen_dict['period'] = index
                                else:
                                    sen_dict['%s' %sen_word] = 1
                                    sen_dict['period'] = index
                                    
                                if word in word_dict.keys():
                                    word_dict['%s' %word] += 1
                                else:
                                    word_dict['%s' %word] = 1

    info_list.append(sen_dict)
    info_list2.append(word_dict)
    
sent = pd.DataFrame(info_list)
word = pd.DataFrame(info_list2)
#del word['period']

result = pd.concat([sent,word],axis = 1)

result['time'] = 0
for index in range(len(start)):
    result['time'][result.period == index] = end[index] 

jpy = pd.read_csv(r'C:\Users\z00013855\Desktop\fx_data\jpyday_return.csv',encoding = 'utf-8')
jpy = jpy.rename(columns={'Time': 'time'})

df2 = result.merge(jpy,on = 'time',how = 'inner')
df2['move_direction'] = np.sign(df2['DailyReturn'])

df3 = df2.groupby('move_direction').mean()
df3.to_csv(r'C:\Users\z00013855\Desktop\treemodel\JU_result.csv',encoding = 'utf-8')