from libraries.SVMTools import SVMTools
from libraries.CNN2label import CNN2label
from libraries.News_pist import News_pist
from libraries.showResults import showResults

import pandas as pd
import numpy as np

if __name__ == '__main__':
    
    hold = 10
    windows = 60
    returnValue = 0.30 * (hold/252)
    priceClass = SVMTools(hold, windows)
    price = priceClass.get_price('2015-01-01','2017-01-01',returnValue)
    
    data = 'zerohedge/zerohedge_source.csv'
    diction = 'dictionary/pist_sentiment.npy'
    cnn = CNN2label(price)
    cnn_df = cnn.get_label()

    newspist = News_pist(price,data,diction,1)
    '''
    pist_x = newspist.data_process()
    pist_x.to_csv("x.txt")
    pist_y = pd.DataFrame(pist_y)
    pist_y.to_csv("y.txt")
    '''
    pist_x = pd.read_csv("x.txt")
    #pist_y = pd.read_csv("y.txt")
    #pist_y = np.asarray(pist_y.iloc[:,1])
    pred_y = priceClass.svm_param_selection(pist_x, 5)
    frame = priceClass.add_label(price, pred_y)
    frame.to_csv("predResult.csv")
    results = showResults(frame, hold, windows)

    pl_result, placc_result = results.PL_SR()
    results.plot_result(pl_result, placc_result)
    
