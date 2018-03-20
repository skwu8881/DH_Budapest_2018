import spacy
import pandas as pd
from nltk import Tree
import nltk
from nltk.tokenize import sent_tokenize
import os
from nltk.util import ngrams
from nltk.tokenize import word_tokenize
import codecs
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
    
# preprocess of news data
data = pd.read_csv('zeroht0319.csv',encoding = 'utf-8')

data['content'] = data['content'].apply(lambda x: x.lower())
data['fomc_word'] = data['content'].apply(lambda x: 1 if 'fomc' in x else 0)

fomc = data.query('fomc_word > 0')
fomc.to_csv('/Users/xiechangrun/Desktop/fomc0319.csv',encoding = 'utf-8')

# load spacy model
nlp = spacy.load('en')

# load entity & sentiment dictionary
entity_cb = pd.read_csv('CTBC_mod5.csv',encoding = 'utf-8')
en_dict = entity_dict(entity_cb)

# load market dictionary (for classification)
market_path = pd.read_csv('market.csv',encoding = 'utf-8')
market_path['entity'] = market_path['entity'].astype(str).str.replace('central#','')
market_dict = entity_dict(market_path)

fomc_news = pd.read_csv('fomc0319.csv',encoding = 'utf-8')
#fomc_news = pd.read_csv('/Users/xiechangrun/Desktop/zdata2015.csv',encoding = 'utf-8')


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
                indice = [j for j,x in enumerate(dfs_list) if 'central#' in x]
                indice_sent = [j for j,x in enumerate(dfs_list) if '@#' in x]
            
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
                        EA = str(dfs_list[a_index].split('_')[1])
                        sen_word = str(dfs_list[b_index].split('_')[0])
                        sen_type = str(dfs_list[b_index].split('_')[1])
            
                        info_dict = OrderedDict()
                        
                        if (m == 0):
                            '''
                            wfile.write('\n')
                            wfile.write('sentence:'+ str(sent) + '\n')
                            '''
                            m+=1
                        
                        if neg_type1 == True:
                            '''
                            if sen_word == gov:
                                wfile.write('========================================'+'\n')
                                wfile.write('type: negation'+'\n')
                                wfile.write('removed entity-sentiment: '+word+'-'+sen_type+'\n')
                            if gov == str(rot):
                                wfile.write('========================================'+'\n')
                                wfile.write('type: negation'+'\n')
                                wfile.write('removed sentence-sentiment: '+word+'-'+sen_type+'\n')
                            '''
                        if neg_type1 == False:
                            '''
                            wfile.write('========================================'+'\n')
                            wfile.write('market:'+market_pin+'\n')
                            wfile.write('entity:'+word+'  '+EA+ '\n')
                            wfile.write('sentiment:'+sen_word+'  '+ sen_type + '\n')
                            '''
                            eas = str(dfs_list[a_index].split('_')[1]+dfs_list[b_index].split('_')[1])
                            eas = eas.split('#')[1]+eas.split('#')[-1]
                            if  eas in eas_count.keys():
                                eas_count['%s' %eas]+=1
                            else:
                                eas_count['%s' %eas]=1
                            
                            ea = str(dfs_list[a_index].split('_')[1])
                            if ea in ea_count.keys():
                                ea_count['%s' %ea]+=1
                            else:
                                ea_count['%s' %ea]=1
                            
                            ea_market.append(market_pin)
    '''
    # write warning sentence
    if len(warning_staff) > 0:
        for stuff in warning_staff:
            wfile.write('\n')
            wfile.write('========================================'+'\n')
            wfile.write('warning sentence: '+stuff+'\n')   
    '''
                
    eas_list.append(eas_count)
    ea_list.append(ea_count)
    #wfile.close()
    count += 1

    if count % 1000 == 0:
        print(count)

eas_frame = pd.DataFrame(eas_list)
ea_frame = pd.DataFrame(ea_list)
ea_marketFrame = pd.DataFrame(ea_market,columns=['market'])

time_frame = fomc_news['time'].astype(str).str[:10]
result = pd.concat([time_frame, ea_frame,ea_marketFrame], axis=1)
complex_result = pd.concat([time_frame, eas_frame,ea_marketFrame], axis=1)

complex_result.fillna(0,inplace=True)
complex_result.to_csv('complex_date_freq2.csv',encoding = 'utf-8')

result.fillna(0,inplace=True)
result.to_csv('word_date_freq2.csv',encoding = 'utf-8')

ea_sum = result.sum()
word_freq = ea_sum.to_frame().reset_index()
word_freq = word_freq.rename(columns= {0: 'freq','index':'word'})
word_freq = word_freq.drop(word_freq.index[[0,1]])
word_freq['word'] = word_freq['word'].astype(str).str.split('#').str[1]
word_freq['freq'] = word_freq['freq'].astype(float)
#word4plot = word_freq.query('freq > 4') 
word_freq.to_csv('word_freq2.csv',encoding = 'utf-8')

word_dict = word_freq.set_index('word')['freq'].to_dict()
              