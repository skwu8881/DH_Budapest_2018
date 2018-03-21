import pandas as pd
import pandas_datareader.data as web
from sklearn import preprocessing
import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn import svm
from sklearn.svm import SVR

class SVMTools():
	def __init__(self, hold, window):
		# hold must be less than window
		self.h = hold
		self.w = window

	def get_price(self, startDate, endDate, return_ratio):
	    '''
	           time  jpus_price   return   true_label
	    1 2016-01-04   119.30        NaN           0
	    2 2016-01-05   118.95  -0.002934          -1
	    3 2016-01-06   118.54  -0.003447          -1
	    
	    '''
	    start = pd.to_datetime(startDate)
	    end = pd.to_datetime(endDate)

	    forex_df = web.DataReader("DEXJPUS", 'fred', start, end)
	    forex_df.reset_index(level=0, inplace=True)
	    forex_df.rename(columns={'DATE':'time','DEXJPUS':'jpus_price'}, inplace=True)
	    price = forex_df.dropna()

	    price['return'] = (price['jpus_price'] - price['jpus_price'].shift(self.h)) / price['jpus_price'].shift(self.h)
	    price['true_label'] = price['return'].apply(lambda x: 1 if x > return_ratio else -1 if x < -return_ratio else 0)
	    price['time'] = pd.to_datetime(price['time'])
	    price.reset_index(drop = True,inplace = True)
	    
	    self.y = price['true_label'] 

	    return price

	def svm_param_selection(self, X, nfolds):
	    scaler = preprocessing.StandardScaler().fit(X)
	    X = scaler.transform(X)

	    #idx = int(0.6 * X.shape[0])
	    pred_y = [np.nan for i in range(self.h+self.w+1)]
	    allRun = X.shape[0]-self.w-1
	    for idx in range(self.h, allRun):
		    train_x = X[idx:(idx+self.w)]
		    train_y = self.y[idx:(idx+self.w)]
		    '''
		    kernels = ['rbf', 'linear']
		    Cs = np.linspace(0.01,2,20)
		    gammas = np.linspace(0.01,1,20)
		    param_grid = {'kernel':kernels, 'C': Cs, 'gamma' : gammas}
		    grid_search = GridSearchCV(svm.SVC(), param_grid, cv=nfolds)
		    grid_search.fit(train_x, train_y)    
		    print(grid_search.best_params_)
		    text_file = open("best_params.txt", "a")
		    text_file.write(str(grid_search.best_params_))
		    text_file.close()
		    temp_y = grid_search.predict(X[idx+self.w+1])
			'''
		    model = svm.SVC(kernel='rbf', C=0.01, gamma=0.01)
		    model.fit(train_x, train_y)
		    temp_y = model.predict(X[idx+self.w+1])
		    pred_y.append(temp_y)
		
	    return pred_y
		
	def add_label(self, price, label):
	    slabel = pd.Series(label, name='label')
	    frame = price.join(slabel)
	    return frame

	def SVR():
	    pass