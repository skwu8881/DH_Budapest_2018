import gensim
import logging
import numpy
import re
import csv
import multiprocessing
from functools import partial
from nltk.corpus import stopwords
from datetime import datetime

### define global variables
model = None
posWords = []
negWords = []

### models = Word2Vec Model
### posWords_path, negWords_path >> one-line-string file ('xxx,ooo,xox,...')
def read_models(model_path, posWords_path, negWords_path):
    #load model
    global model
    model = gensim.models.Word2Vec.load(model_path)

    #read main-Words
    with open(posWords_path) as f:
        content = f.readlines()
        global posWords
        posWords = str(content[0]).split(',')    
    with open(negWords_path) as f:
        content = f.readlines()
        global negWords
        negWords = str(content[0]).split(',')
    
    logging.info('read models success!\n')
    

#preprocessing text
def text_preprocess(txt):
    stop_words = set(stopwords.words('english'))
    words = re.sub(r'[^\w]', ' ', str(txt)).lower().split()
    valid_words = []
    for word in words:
        if word not in stop_words:
            valid_words.append(word)
    return valid_words

#temporarily deprecated...
def eul_dist(wordA, wordB):
	global model
    dist = numpy.linalg.norm(model[wordA] - model[wordB]))
	return dist

#get the Positive-score
def countPos(word, threshold):
    global posWords
    global model
    pos_score = 0.0
    pos_count = 0
    for posWord in posWords:
        try:
            rate = model.similarity(word, posWord)
            if rate > -threshold and rate < threshold:
                continue
            else:
                pos_score += rate
                pos_count += 1
        except:
            continue
    #dealing with 'x/0' exception
    if pos_count == 0:
        pos_count = 1
        
    return (pos_score/pos_count)

#get the Negative-score
def countNeg(word, threshold):
    global negWords
    global model
    neg_score = 0.0
    neg_count = 0
    for negWord in negWords:
        try:
            rate = model.similarity(word, negWord)
            if rate > -threshold and rate < threshold:
                continue
            else:
                neg_score += rate
                neg_count += 1
        except:
            continue
    #dealing with 'x/0' exception
    if neg_count == 0:
        neg_count = 1
            
    return (neg_score/neg_count)
    

#rating Algorithm
def scoreAlgo(words, threshold=0.17):
    #initialze multiprocessing
    threads = multiprocessing.cpu_count()*2
    pos_score = 0.0
    neg_score = 0.0
    
    #calculate positive score
    with multiprocessing.Pool(threads) as pool_pos:
        res = pool_pos.map(partial(countPos, threshold=threshold), words)
        pos_score = sum(res)
    #calculate negative score
    with multiprocessing.Pool(threads) as pool_neg:
        res = pool_neg.map(partial(countNeg, threshold=threshold), words)
        neg_score = sum(res)        
    
    return {'pos_score': pos_score, 'neg_score': neg_score}
    

#rate the Article
### article_path >> articles source = {'time': time-format, 'content': string, [optional: 'title': string]}
def rateArticles(article_path, amount=-1):
    output = []
    with open(article_path) as f:
        rd = csv.DictReader(f)
        it = 1
        for _data in rd:
            
            logging.info('Article #%5d > analyzing...  '%(it))
            
            #preprocess text
            valid_words = text_preprocess(str(_data['content']))
            
            #get the scores
            scores = scoreAlgo(words=valid_words)
            
            #simply calculate the final score
            main_score = scores['pos_score']-scores['neg_score']
            
            #if score >= 0.0 then print 'positive', otherwise 'negative'
            #...how about the type 'neutral'?
            result = '+' if main_score >= 0.0 else '-'
            
            #get timestamps
            time_stamp = str(_data['time']).replace(',','')
            
            #append to output array    
            output.append([str(it), time_stamp, main_score, result])
                            
            logging.info('Article #%5d > completed!'%(it))
            
            #deadline = datetime(2017,3,31,9,30,0,0) #set due time
            if amount > 0 and it == amount:
                break
            #elif datetime.now() > deadline: #break when time-exceed
                #break
            else:
                it += 1
                
    return output
         

if __name__ == '__main__':
    #set logging pattern
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    #multiprocess preprocess
    multiprocessing.freeze_support()
    ###main
    read_models(model_path='w2v_model/zerohedge-500-2-model', \
                posWords_path='dictionary/posWords', \
                negWords_path='dictionary/negWords')
    
    results = rateArticles(article_path='forexfactory/forexfactory_source.csv')

    ###save outputs
    f = open('forexfactory/forexfactory_result-500-2.csv','w')
    f.write('id,time,score,result\n')
    for r in results:
        for c in range(len(r)):
            if c > 0:
                f.write(',')
            f.write(str(r[c]))
        f.write('\n')
    f.close()
    logging.info('output results > done!')



