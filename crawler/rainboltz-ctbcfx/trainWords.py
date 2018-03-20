import csv
import gensim, logging
import sys
import re

class SetupTrainData():
    def __init__(self):
        #preprocess
        csv.field_size_limit(sys.maxsize)
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    ### main_path >> {'Word': string, 'Positive': 0 or greater, 'Negative': 0 or greater}
    ### pos_path, neg_path = output path.
    def createWordLists(self, main_path, pos_path, neg_path):
        #input raw datas
        posWords = []
        negWords = []
        with open(main_path) as f:
            rd = csv.DictReader(f)
            for _data in rd:
                if int(_data['Positive']) > 0:
                    posWords.append(str(_data['Word']).lower())
                elif int(_data['Negative']) > 0:
                    negWords.append(str(_data['Word']).lower())
        #output main-words
        wt = open(pos_path,'w')
        for p in range(len(posWords)):
            if p > 0:
                wt.write(',')
            wt.write(posWords[p])
        wt.close()
        wt = open(neg_path,'w')
        for n in range(len(negWords)):
            if n > 0:
                wt.write(',')
            wt.write(negWords[n])
        wt.close()

    ### data_path >> {'content': a article(string)}
    ### word2vec arguments please visit website...
    def trainWord2Vec(self, data_path, output_name='', _size=1000, _window=2, _min_count=5, _workers=4):
        #get trainer-content
        trainData = []
        with open(data_path) as f:
            rd = csv.DictReader(f)
            for _data in rd:
                sentence = re.sub(r'[^\w]', ' ', str(_data['content'])).lower().split()
                trainData.append(sentence)
        #start training
        model = gensim.models.Word2Vec(trainData, \
                    size=_size, window=_window, min_count=_min_count, workers=_workers)
        if output_name == '':
            output_name = data_path + '-model'
        model.save(output_name)        
    
    
if __name__ == '__main__':
    mydata = SetupTrainData()
    mydata.createWordLists('dictionary/McDonaldDictionary.csv','dictionary/posWords','dictionary/negWords')
    mydata.trainWord2Vec(_size=500, _window=2, data_path='forexfactory/forexfactory_source.csv', \
                                                output_name='w2v_model/forexfactory-500-2-model')
