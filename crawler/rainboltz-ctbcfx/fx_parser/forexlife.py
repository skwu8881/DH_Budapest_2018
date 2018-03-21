import simpledate
from collections import OrderedDict
import pandas as pd
from pyquery import PyQuery as pq

info = []
domain = 'http://www.forexlive.com/Headlines/'
fr_time = pd.to_datetime('2011-01-01')

for i in range(0,25):
    if i == 0:
        urls = 'http://www.forexlive.com/'
        q = pq(urls)
        url_nodes = q('div.col-md-10.col-xs-10.axa-aprev-cont h2 a')
    else:
        urls = domain +str(i)
        q = pq(urls)
        url_nodes = q('div.col-lg-11.col-md-11.col-xs-10.axa-aprev-cont h3 a')
    for each in url_nodes:
        try:
            news_title = pq(each).attr('title').split(':')[1]
            if 'orderboard' in news_title:
                continue
            else:
                news_url = 'http:'+str(pq(each).attr('href'))
                news_q = pq(news_url)

                times = str(pd.to_datetime(news_q('span.micro').parent('time').text()))
                temp = simpledate.SimpleDate(times+' EDT').utc
                utc_time = pd.to_datetime(str(temp).split('U')[0])
                
                if utc_time > fr_time:
                    info_dict = OrderedDict()
                    info_dict['time'] = utc_time
                    info_dict['author'] = news_q('.pull-right a:nth-child(2)').text()
                    info_dict['category'] = news_q('.pull-right a:nth-child(4)').text()
                    info_dict['news_title'] = news_title
                    info_dict['content'] = news_q('.col-md-10.col-sm-10.col-xs-10.artbody').text()
                    info_dict['url'] = news_url
                    info.append(info_dict)
        except:
            continue
    if i % 10 == 0:
        print('page',i,'is done.')

data = pd.DataFrame(info)
data.to_csv(r'/Users/xiechangrun/Desktop/forexlive.csv',encoding='utf-8',index=None)