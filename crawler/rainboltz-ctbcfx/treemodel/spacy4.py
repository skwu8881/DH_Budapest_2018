import spacy
import nltk
import codecs
import re
import configparser
import sys, os
import numpy as np
import pandas as pd
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import Tree
from nltk.util import ngrams
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
	
def tok_format(tok):
	return "_".join([tok.orth_,tok.ent_type_]) # tok.lemma_, 
	
def to_nltk_tree(node):
	if node.n_lefts + node.n_rights > 0:
		return Tree(tok_format(node), [to_nltk_tree(child) for child in node.children])
	else:
		return tok_format(node)
	
def tp_format(tok):
	return ' '.join([tok.pos_,tok.lemma_])

def to_tp_tree(node):
	if node.n_lefts + node.n_rights > 0:
		return Tree(tp_format(node), [to_tp_tree(child) for child in node.children])
	else:
		return tp_format(node)

def traverseTree(tree):
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

def getCTBC_MOD():
	pass

nlp = spacy.load('en')

entity_cb = pd.read_csv('CTBC_mod5.csv',encoding = 'utf-8')
en_dict = entity_dict(entity_cb)

market_path = pd.read_csv('market.csv',encoding = 'utf-8')
market_path['entity'] = market_path['entity'].astype(str).str.replace('central#','')
market_dict = entity_dict(market_path)
#notify_dict = {'central#rate':['hike','cut','go up','go down'],'central#inflation':['increase','decrease','go up','go down']}
#mapping_dict = {'hike':'up','cut':'down','go up':'up','go down':'down'}


fomc_news = pd.read_csv('fomc0319.csv',encoding = 'utf-8')

txt_list = []
for root, dirs, files in os.walk("new_central"):
	for file in files:
		if '.txt' in file:
			txt_list.append(os.path.join(root, file))

count_list = []
eas_list = []
gg_list = []
market_list = []
negterm = ["n't",'no','not','never','none','nothing','nobody','noone','nowhere','without','hardly',
		   'barely','rarely','seldom','against','minus']
neg_dep_list = ['det','prt','advmmod','dobj','nsubj','dep']
mark_list = ['that','although','while','to']

n = 0
for each in txt_list:
	warning_staff = []
	market_pin = ''
	eas_count={}
	ea_count={}

	try:
		rfile = codecs.open(each, "r", "big5")
		text2 = ''.join(x for x in rfile.readlines())
		code_type = 0
	except:
		rfile = codecs.open(each, "r", "utf-8")
		text2 = ''.join(x for x in rfile.readlines())
		code_type = 1
	#print(each,code_type)
		
	rfile.close()
	
	root2 = "/Users/xiechangrun/Desktop/pycsv_files/new_test"
	save_file = os.path.join(root2,each.split('/')[-1])
	#print(save_file)
	
	
	if code_type == 1:
		wfile = codecs.open(save_file,'w','utf-8')  
	if code_type == 0:
		wfile = codecs.open(save_file,'w','big5')
		
	subsent_list = []
	sent_list = sent_tokenize(text2)
	
	for each in sent_list:
		wfile.write(each+ '\n')
		for subsent in each.split(','):
			if len(subsent.split(' ')) > 1: 
				for smaller_sent in subsent.split(':'):  
					subsent_list.append(smaller_sent)

					
	entity_list = list(en_dict.keys())
	
	#remove overlap
	for each in subsent_list:
		each = each.lower()
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
					pass
		
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
	
		doc = nlp(each)
		#doc = nlp("the evolution of oil prices and the euro exchange rate points to lower inflation than the conditioning assumptions underlying the ecb staff¡šs most recent published forecasts.")
		
		try:
			matcher(doc)
		except:
			print(doc,'is unavalable.')
			continue
			
		dfs_list = []
		for sent in doc.sents:
			#sent = nlp("draghi to encourage further currency appreciation and/or higher long rates.")				
			rot = [w for w in sent if w.head is w][0] #root
			gg_list = []
			neg_type1 = False
			for wordss in sent:
				typed_d = ''.join([str(wordss.dep_),'(',str(wordss.head),',',str(wordss),')'])
				Td = typed_d.split('(')[0]
				gov = typed_d.split('(')[1].split(',')[0]
				dep = typed_d.split(',')[1].split(')')[0]
				gg_list.append(''.join([str(wordss.dep_),'(',str(wordss.head),',',str(wordss),')']))
				
				if (Td == 'neg') & (gov in entity_list):
					neg_type1 = True

				if (Td in neg_dep_list) & (dep in negterm) & (gov in entity_list):
					neg_type1 = True

				if (Td == 'neg') & (gov == str(rot)) & (rot.pos_ == 'VERB'):
					#print(sent)
					neg_type1 = True

				if (Td in neg_dep_list) & (dep in negterm) &(gov == str(rot)) & (rot.pos_ == 'VERB'):
					#print(sent)
					neg_type1 = True
				
				#if (Td == 'mark') | (Td == 'aux') & (dep in mark_list):
					#print(gov,dep)
					#print(sent)
					
			
			dfs_list = []
			traverseTree(to_nltk_tree(sent.root))
			#to_nltk_tree(sent.root).pretty_print()

			#nltk_tree_list.append(to_tp_tree(sent.root))
			print(dfs_list)
		
			for word in dfs_list:
				indice = [j for j,x in enumerate(dfs_list) if 'central#' in x]
				indice_sent = [j for j,x in enumerate(dfs_list) if '@#' in x]
			
			length = len(sent) / 5 + 1
						
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
							wfile.write('\n')
							wfile.write('sentence:'+ str(sent) + '\n')
							m+=1
						
						if neg_type1 == True:
							wfile.write('========================================'+'\n')
							wfile.write('type: negation'+'\n')
							if sen_word == gov:
								wfile.write('removed entity-sentiment: '+word+'-'+sen_type+'\n')
							if gov == str(rot):
								wfile.write('removed sentence-sentiment: '+word+'-'+sen_type+'\n')
						
						if neg_type1 == False:
							#if sen_word in notify_dict['%s' %word]:
							#	print(word,mapping_dict[sen_word])
							#else:
							#	continue
							wfile.write('========================================'+'\n')
							wfile.write('market:'+market_pin+'\n')
							wfile.write('entity:'+word+'  '+EA+ '\n')
							wfile.write('sentiment:'+sen_word+'  '+ sen_type + '\n')
					
							eas = str(dfs_list[a_index].split('_')[1]+dfs_list[b_index].split('_')[1])
							eas = eas.split('#')[1]+eas.split('#')[-1]
							
							info_dict['article'] = n
							info_dict['aspect'] = eas.split('@')[0]
							info_dict['sentiment'] = eas.split('@')[1]
							info_dict['market'] = market_pin
							info_dict['date'] = pd.to_datetime('2017-07-12')
									 
							eas_list.append(info_dict)
						
			'''
			for idx in indice:
				for index in indice_sent:
					if abs(idx-index) <= length:
						
						k += 1
						word = str(dfs_list[idx].split('_')[0])
						EA = str(dfs_list[idx].split('_')[1])
						sen_word = str(dfs_list[index].split('_')[0])
						sen_type = str(dfs_list[index].split('_')[1])
						
						info_dict = OrderedDict()
						
						if (m == 0) and (k > 0):
							wfile.write('\n')
							wfile.write('sentence:'+ str(sent) + '\n')
							m+=1
						
						if neg_type1 == True:
							if sen_word == gov:
								wfile.write('========================================'+'\n')
								wfile.write('type: negation'+'\n')
								wfile.write('removed entity-sentiment: '+word+'-'+sen_type+'\n')
							if gov == str(rot):
								wfile.write('========================================'+'\n')
								wfile.write('type: negation'+'\n')
								wfile.write('removed sentence-sentiment: '+word+'-'+sen_type+'\n')
						
						if neg_type1 == False:
							wfile.write('========================================'+'\n')
							wfile.write('market:'+market_pin+'\n')
							wfile.write('entity:'+word+'  '+EA+ '\n')
							wfile.write('sentiment:'+sen_word+'  '+ sen_type + '\n')
						
						
							eas = str(dfs_list[idx].split('_')[1]+dfs_list[index].split('_')[1])
							eas = eas.split('#')[1]+eas.split('#')[-1]
							
							info_dict['article'] = n
							info_dict['aspect'] = eas.split('@')[0]
							info_dict['sentiment'] = eas.split('@')[1]
							info_dict['market'] = market_pin
									 
							eas_list.append(info_dict)
							#eas_list.append(eas)
							#count_list.append(n)
							

								
	# write warning sentence
	if len(warning_staff) > 0:
		for stuff in warning_staff:
			wfile.write('\n')
			wfile.write('========================================'+'\n')
			wfile.write('warning sentence: '+stuff+'\n')   
	'''
	wfile.close()
	n += 1

eas_frame = pd.DataFrame(eas_list)
#ea_frame = pd.DataFrame(ea_list,columns = ['ea'])
#count_frame = pd.DataFrame(count_list,columns = ['article'])
#ea_marketFrame = pd.DataFrame(ea_market,columns=['market'])
#result = pd.concat([count_frame,ea_frame,ea_marketFrame], axis=1)
#complex_result = pd.concat([count_frame,eas_frame,ea_marketFrame], axis=1)

#result.fillna(0,inplace=True)
eas_frame.fillna(0,inplace=True)

#result.to_csv('/Users/xiechangrun/Desktop/result_freq.csv',encoding = 'utf-8')
eas_frame.to_csv('complex_freq.csv',encoding = 'utf-8',index=None)

