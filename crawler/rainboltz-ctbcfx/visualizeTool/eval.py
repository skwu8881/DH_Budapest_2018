import gensim
import logging
import numpy
import re
import csv
from nltk.corpus import stopwords

### define global variables
model = None
posWords = []
negWords = []
stopwordset = set(stopwords.words('english'))

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
    words = re.sub(r'[^\w]', ' ', str(txt)).lower().split()
    
    return words

#deprecated method
def eul_dist(wordA, wordB):
    global model
    dist = numpy.linalg.norm(model[wordA] - model[wordB])
    
    return dist

#get the Positive-score
def countPos(word, threshold):
    global stopwordset
    if word in stopwordset:
        return 0.0
        
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
    global stopwordset
    if word in stopwordset:
        return 0.0
    
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
    

#rate the Article
### article_path >> articles source = {'time': time-format, 'content': string, [optional: 'title': string]}
def rateArticle(article, w_th, c_th, r_th):

    logging.info('Article analyzing... ')
    
    word_threshold = w_th
    
    color_threshold = c_th
    rage_threshold = r_th

    outputString = ""
    
    #preprocess text
    words = text_preprocess(str(article))
    
    for word in words:
        posScore = countPos(word, word_threshold)
        negScore = countNeg(word, word_threshold)
        final_score = posScore - negScore
        
        hint = '<a href="#" data-toggle="tooltip" data-placement="top" title="'+str(final_score)+'">'
        
        if final_score < -color_threshold or final_score > color_threshold:
            if final_score > rage_threshold:
                outputString += '<pospos>'+hint+str(word)+'</a> </pospos>'
            elif final_score < -rage_threshold:
                outputString += '<negneg>'+hint+str(word)+'</a> </negneg>'
            elif final_score > 0.0:
                outputString += '<pos>'+hint+str(word)+'</a> </pos>'
            elif final_score < 0.0:
                outputString += '<neg>'+hint+str(word)+'</a> </neg>'
        else:
            outputString += '<nor>'+hint+str(word)+'</a> </nor> '
        
    
    return outputString
            
                
         

def RUN_EVAL(inputstr, w_th, c_th, r_th):
    #set logging pattern
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    
    ###main
    read_models(model_path='zerohedge-500-2-model', \
                posWords_path='posWords', \
                negWords_path='negWords')
    
    result = rateArticle(inputstr, w_th, c_th, r_th)
    
    return result
    