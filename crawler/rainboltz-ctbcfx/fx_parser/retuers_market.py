from pyquery import PyQuery as pq
import pandas as pd
from collections import OrderedDict
import multiprocessing
import simpledate

def get_url(MainPage,mode):
    '''
    mode = 0 parse all article
    mode = 1 parse latest article
    '''
    url_list = []
    if mode == 0:
        for i in range(1,40):
            main_url = MainPage + str(i) + '&pageSize=10'
            q = pq(main_url)
            url_node = q('.story-content a')
            for each in url_node:
                url = 'http://www.reuters.com' + str(pq(each).attr('href'))
                url_list.append(url)
    else:
        for i in range(1,10):
            main_url = MainPage + str(i) + '&pageSize=10'
            q = pq(main_url)
            url_node = q('.story-content a')
            for each in url_node:
                url = 'http://www.reuters.com' + str(pq(each).attr('href'))
                url_list.append(url)
    
    return url_list

def get_content(url):
    global frtime
    rt_dict = OrderedDict()
    
    q = pq(url)
    edt_time = str(pd.to_datetime(q('span.timestamp').text().replace('| ','')))
    temp = simpledate.SimpleDate(edt_time+' EDT').utc
    utc_time = pd.to_datetime(str(temp).split('U')[0])
    if utc_time > frtime:
        rt_dict['title'] = q('.article-headline').text()
        rt_dict['time'] = utc_time
        rt_dict['content'] = q('#article-text p').text()
    return rt_dict

def time_filter(olddf,newdf):
    maxtime = olddf['time'].max()
    newdf = newdf[newdf['time'] > maxtime]
    return newdf

if __name__ == '__main__':
    '''
    olddata = pd.read_csv('/Users/xiechangrun/Desktop/rt_after0423.csv',encoding = 'utf-8')
    
    tmp = olddata['time'].max()
    frtime = pd.to_datetime(str(tmp).split('U')[0])
    '''
    #firsttime
    frtime = pd.to_datetime('2011-01-01')
    
    MainPage = 'http://www.reuters.com/news/archive/marketsNews?view=page&page='
    url_all = get_url(MainPage,1)
    
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    results = pool.map(get_content,url_all)
    
    scraped_data = []
    for each in results:
        scraped_data.append(each)
        
    data = pd.DataFrame(scraped_data)
    data.dropna(inplace = True)
    
    '''
    data_new = time_filter(olddata,data)
    data = data.append(data_new)
    '''
    data.to_csv('/Users/xiechangrun/Desktop/rt_after0423.csv',encoding = 'utf-8',index = None)

