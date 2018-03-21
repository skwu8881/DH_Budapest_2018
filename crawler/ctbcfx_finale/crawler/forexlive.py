import simpledate
from collections import OrderedDict
import pandas as pd
from pyquery import PyQuery as pq
import sys, os
import configparser

class Forexlive_Crawler:
	def __init__(self, startpage=0, stoppage=None):
		#initialize paths and constants
		#conf = os.path.abspath(os.path.join(sys.path[0], os.pardir))
		self.config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
		#self.config.read(conf + '/config.ini')
		self.config.read(sys.path[0] + '/config.ini')
		
		if stoppage != None:
			self.startpage = startpage
			self.stoppage = stoppage
		else:
			self.startpage = 0
			self.stoppage = int(self.config['CNBC']['LastPage'])
		
	def execute(self, output_csv=True):
		info = []
		for i in range(self.startpage,self.stoppage+1):
			if i == 0:
				urls = self.config['FOREXLIVE']['HomeURL']
				q = pq(urls)
				url_nodes = q('div.col-md-10.col-xs-10.axa-aprev-cont h2 a')
			else:
				urls = self.config['FOREXLIVE']['QueryURL']+ "/" +str(i)
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

						temp = str(pd.to_datetime(news_q('span.micro').parent('time').text()))
						utc_time = pd.to_datetime(str(temp).split('G')[0])
						
						fr_time = pd.to_datetime('2011-01-01')
						if utc_time > fr_time:
							info_dict = OrderedDict()
							info_dict['time'] = utc_time
							info_dict['author'] = news_q('.pull-right a:nth-child(2)').text()
							#info_dict['category'] = news_q('.pull-right a:nth-child(4)').text()
							info_dict['title'] = news_title
							info_dict['content'] = news_q('.col-md-10.col-sm-10.col-xs-10.artbody').text()
							#info_dict['url'] = news_url
							info.append(info_dict)
				except:
					continue
			if i % 10 == 0:
				print('page#'+str(i),'crawled...')

		data = pd.DataFrame(info)		
		first_count = len(data.index)
		data.dropna(inplace = True)
		data.drop_duplicates(subset = 'title',inplace=True)
		second_count = len(data.index)
		
		print('removing duplicates: before= %d | after= %d\n'%(first_count,second_count))
		
		if output_csv:
			data.to_csv(self.config['FOREXLIVE']['OutputPath'],encoding='utf-8',index=None)
			
		return data