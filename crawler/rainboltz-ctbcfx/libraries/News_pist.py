import logging
import pandas as pd
import numpy as np
from nltk.util import ngrams
from nltk.tokenize import word_tokenize

class News_pist():
    def __init__(self,price,data,diction,option):
        '''
        option = 0 if title
        option = 1 if content
        '''
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
        #self.splitter = nltk.data.load('tokenizers/punkt/english.pickle')
        self.price = price
        self.data = pd.read_csv(data,encoding='utf-8')
        self.diction = np.load(diction).item()
        self.option = option

    def get_ngrams(self, text, n):
        n_grams = ngrams(word_tokenize(text), n)
        phrase = [' '.join(grams) for grams in n_grams]
        return phrase

    def check_ngram(self,diction,phrase):
        n = 0
        label_dict = {}
        for sent in phrase:
            if sent in diction.keys():
                label_dict['%s' % sent] = diction[sent]
                n += diction[sent]
        return label_dict,n

    def get_score(self):
        data = self.data
        labellist = []
        m = 0
        if self.option == 0:
            for article in data['title']:
                score = 0
                if m % 1000 == 0:
                    logging.info('Article #%5d > analyzing...  ' % (m))
                for i in range(1, 4):
                    label_dict, n = self.check_ngram(self.diction, self.get_ngrams(article, i))
                    labellist.append(label_dict)
                    score += n
                data.loc[m, 'score'] = score
                m += 1
        if self.option == 1:
            for article in data['content']:
                score = 0
                if m % 1000 == 0:
                    logging.info('Article #%5d > analyzing...  ' % (m))
                for i in range(1, 4):
                    label_dict, n = self.check_ngram(self.diction, self.get_ngrams(article, i))
                    labellist.append(label_dict)
                    score += n
                data.loc[m, 'score'] = score
                m += 1
        if self.option == 0:
            data['word_count'] = data['title'].apply(lambda x: len(x.split()))
        if self.option == 1:
            data['word_count'] = data['content'].apply(lambda x: len(x.split()))
    
        data['mod_score'] = data['score'] / data['word_count']
        data['result'] = data['mod_score'].apply(lambda x: '+' if x > 0 else '-')
        
        return data

    def data_process(self):
        news = self.get_score()
        news['time'] = pd.to_datetime(news['time'])
        news['time'] = news['time'].astype(str).str[0:10]
        news['time'] = pd.to_datetime(news['time'])
        news['mod_score'] = news['mod_score'].astype('float32')

        neg_news = news[news.result == '-']

        neg_news['neg_mean'] = neg_news.groupby('time')['mod_score'].transform('mean')
        neg_news['neg_num'] = neg_news.groupby('time')['mod_score'].transform('count')
        neg_news['neg_std'] = neg_news.groupby('time')['mod_score'].transform('std')

        neg_news.drop_duplicates(subset='time', inplace=True)
        neg_news = neg_news[['time', 'neg_mean', 'neg_num', 'neg_std']]

        pos_news = news[news.result == '+']

        pos_news['pos_mean'] = pos_news.groupby('time')['mod_score'].transform('mean')
        pos_news['pos_num'] = pos_news.groupby('time')['mod_score'].transform('count')
        pos_news['pos_std'] = pos_news.groupby('time')['mod_score'].transform('std')

        pos_news.drop_duplicates(subset='time', inplace=True)
        pos_news = pos_news[['time', 'pos_mean', 'pos_num', 'pos_std']]

        temp = pd.merge(news, pos_news, on='time', how='outer')
        temp2 = pd.merge(temp, neg_news, on='time', how='outer')

        final = pd.merge(temp2, self.price, on='time')
        final = final.drop_duplicates(subset='time')
        final = final.reset_index(drop=True)

        col4keep = ['time', 'neg_mean','neg_num','neg_std','pos_mean','pos_num','pos_std','true_label']
        cols = [col for col in final.columns if col in col4keep]

        final = final[cols]
        final.sort_values(by='time',inplace = True)
        final = final.reset_index(drop=True)
        
        X = final.iloc[:,1:7]
        return X
