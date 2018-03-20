from pyquery import PyQuery as pq
import pandas as pd
from collections import OrderedDict
import multiprocessing
import simpledate
import pytz
from datetime import datetime,timedelta

def get_url(MainPage,mode):
    url_list = []
    if mode == 0:
        for i in range(0,542):
            main_url = MainPage + str(i)
            q = pq(main_url)
            url_node = q('#pipeline_assetlist_0 .headline a')
            for each in url_node:
                url = 'http://www.cnbc.com'+ str(pq(each).attr('href'))
                url_list.append(url)
    else:
        for i in range(0,10):
            main_url = MainPage + str(i)
            q = pq(main_url)
            url_node = q('#pipeline_assetlist_0 .headline a')
            for each in url_node:
                url = 'http://www.cnbc.com'+ str(pq(each).attr('href'))
                url_list.append(url)
    
    return url_list

def get_content(url):
    global frtime
    # 一日內的新聞會以xx hours ago顯示,先省略不看
    rt_dict = OrderedDict()

    q = pq(url)
    
    if 'ours' in q('time.datestamp').text():
        number = int(str(q('time.datestamp').text())[0:2])
        trans_time = datetime.now(pytz.timezone('America/New_York'))
        edt_time = str(trans_time - timedelta(hours = number))[0:17]
    
    else:
        edt_time = str(pd.to_datetime(q('time.datestamp').text().replace('| ','')))
    
    temp = simpledate.SimpleDate(edt_time+' EDT').utc
    utc_time = pd.to_datetime(str(temp).split('U')[0])
            
    if utc_time > frtime:
        rt_dict['title'] = q('.title').text()
        rt_dict['time'] = utc_time
        try:
            rt_dict['content'] = q('.content p').text()
        except:
            rt_dict['content'] = 'none'
            
    return rt_dict

def time_filter(olddf,newdf):
    maxtime = olddf['time'].max()
    newdf = newdf[newdf['time'] > maxtime]
    return newdf

if __name__ == '__main__':
    '''
    olddata = pd.read_csv('/Users/xiechangrun/Desktop/cnbc_us.csv',encoding = 'utf-8')
    
    tmp = olddata['time'].max()
    frtime = pd.to_datetime(str(tmp).split('U')[0])
    '''
    #firsttime
    frtime = pd.to_datetime('2011-01-01')
    
    MainPage = 'http://www.cnbc.com/us-news/?page='
    url_all = get_url(MainPage,0)
    
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
    data.to_csv('/Users/xiechangrun/Desktop/cnbc_us.csv',encoding = 'utf-8',index = None)

