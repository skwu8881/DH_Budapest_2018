class News_w2v():
    def __init__(self,price):
        self.price = price

    def get_score(self,model_path,pos_path,neg_path,article_path,save_path):
        multiprocessing.freeze_support()
        w2v.read_models(model_path,pos_path,neg_path)
        results = w2v.rateArticles(article_path)
        f = open(save_path, 'w')
        f.write('id,time,score,result\n')
        for r in results:
            for c in range(len(r)):
                if c > 0:
                    f.write(',')
                f.write(str(r[c]))
            f.write('\n')
        f.close()

    def news_preprocess(self,save_path):
        news = pd.read_csv(save_path,encoding = 'utf-8').dropna()
        time_tmp = news['time'].astype(str).str.findall(r'^[^\d\W]* \d* \d*').tolist()
        time_list = []
        for each in time_tmp:
            time_list.append(each[0])
        news['time'] = pd.to_datetime(time_list)
        news['score'] = news['score'].astype('float32')

        neg_news = news[news.result == '-']

        neg_news['neg_mean'] = neg_news.groupby('time')['score'].transform('mean')
        neg_news['neg_num'] = neg_news.groupby('time')['score'].transform('count')
        neg_news['neg_std'] = neg_news.groupby('time')['score'].transform('std')

        neg_news.drop_duplicates(subset='time', inplace=True)
        neg_news = neg_news[['time', 'neg_mean', 'neg_num', 'neg_std']]

        pos_news = news[news.result == '+']

        pos_news['pos_mean'] = pos_news.groupby('time')['score'].transform('mean')
        pos_news['pos_num'] = pos_news.groupby('time')['score'].transform('count')
        pos_news['pos_std'] = pos_news.groupby('time')['score'].transform('std')

        pos_news.drop_duplicates(subset='time', inplace=True)
        pos_news = pos_news[['time', 'pos_mean', 'pos_num', 'pos_std']]

        temp = pd.merge(news, pos_news, on='time', how='outer')
        temp2 = pd.merge(temp, neg_news, on='time', how='outer')

        final = pd.merge(temp2, self.price, on='time')
        final = final.drop_duplicates(subset='time')

        col4keep = ['time', 'neg_mean','neg_num','neg_std','pos_mean','pos_num','pos_std','true_label']
        cols = [col for col in final.columns if col in col4keep]

        final = final[cols]
        final = final.reset_index(drop=True)


        X = final.iloc[:,1:7]
        y = np.ravel(final['true_label'])
        return (X,y)
    
    def svmLabel(self):
        pass