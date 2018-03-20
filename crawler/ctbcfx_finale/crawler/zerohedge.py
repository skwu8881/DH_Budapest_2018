from pyquery import PyQuery as pq
import pandas as pd
from collections import OrderedDict
import simpledate
import sys, os
import configparser
import pytz
from datetime import datetime,timedelta

class Zerohedge_Crawler:
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
			self.stoppage = int(self.config['ZEROHEDGE']['LastPage'])

	def get_url(self):
		url_list = []
		for i in range(self.startpage,self.stoppage+1):
			main_url = self.config['ZEROHEDGE']['QueryURL'] + str(i)
			q = pq(main_url)
			url_node = q('h2 a')
			for each in url_node:
				url = self.config['ZEROHEDGE']['HomeURL']+str(pq(each).attr('href'))
				url_list.append(url)
		
		return url_list

	def get_content(self, url):
		us = pytz.timezone('America/New_York')
		dtfr = datetime.strptime('2011-01-01', '%Y-%m-%d').replace(tzinfo=us)
		frtime = pd.to_datetime(dtfr.astimezone(pytz.utc))
		rt_dict = OrderedDict()

		q = pq(url)
		edt_time = str(pd.to_datetime(q('.submitted_datetime span').text())) #.replace('| ','')))
		us = pytz.timezone('America/New_York')
		dt = datetime.strptime(edt_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=us)
		utc_time = pd.to_datetime(dt.astimezone(pytz.utc))
		if utc_time > frtime:
			rt_dict['title'] = q('.article-list .title').text()
			rt_dict['time'] = utc_time
			rt_dict['content'] = q('.content p').text()
			rt_dict['tag'] = q('.taxonomy-links').text()
		return rt_dict
	'''
	def time_filter(olddf,newdf):
		maxtime = olddf['time'].max()
		newdf = newdf[newdf['time'] > maxtime]
		return newdf
	'''
	def execute(self, output_csv=True):
		url_all = self.get_url()
		
		errors = 0
		index = 1
		scraped_data = []
		for _url in url_all:
			if index%100 == 0:
				print(str(index)+' urls crawled...')
				
			try:
				scraped_data.append(self.get_content(_url))
			except:
				errors += 1
				print('caught an unexpected error <at %s>'%(_url))
			index += 1
			
		data = pd.DataFrame(scraped_data)
		first_count = len(data.index)
		data.dropna(inplace = True)
		data.drop_duplicates(subset = 'title',inplace=True)
		second_count = len(data.index)
		print('removing duplicates: before= %d | after= %d\n'%(first_count,second_count))
		'''
		data_new = time_filter(olddata,data)
		data = data.append(data_new)
		'''
		if output_csv:
			data.to_csv(self.config['ZEROHEDGE']['OutputPath'],encoding = 'utf-8',index = None)
		return data
