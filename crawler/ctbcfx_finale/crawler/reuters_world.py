from pyquery import PyQuery as pq
import pandas as pd
from collections import OrderedDict
import simpledate
import pytz
from datetime import datetime,timedelta
import configparser
import sys, os

class ReutersWorld_Crawler:
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
			self.stoppage = int(self.config['REUTERS']['LastPage_World'])
			
	def get_url(self):
		url_list = []
		for i in range(self.startpage,self.stoppage+1):
			main_url = self.config['REUTERS']['QueryURL_World'] + str(i) + '&pageSize=10'
			q = pq(main_url)
			url_node = q('.story-content a')
			for each in url_node:
				url = self.config['REUTERS']['HomeURL'] + str(pq(each).attr('href'))
				url_list.append(url)
		return url_list

	def get_content(self, url):
		us = pytz.timezone('America/New_York')
		dtfr = datetime.strptime('2011-01-01', '%Y-%m-%d').replace(tzinfo=us)
		frtime = pd.to_datetime(dtfr.astimezone(pytz.utc))
		rt_dict = OrderedDict()
		
		q = pq(url)
		raw_time = q('.ArticleHeader_date_V9eGk').text().split('/')
		raw_time = raw_time[0] + raw_time[1]
		edt_time = str(pd.to_datetime(raw_time))
		us = pytz.timezone('America/New_York')
		dt = datetime.strptime(edt_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=us)
		utc_time = pd.to_datetime(dt.astimezone(pytz.utc))
		if utc_time > frtime:
			rt_dict['title'] = q('title').text()
			rt_dict['time'] = utc_time
			rt_dict['content'] = q('.ArticleBody_body_2ECha').text()
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
		
		print('[complete]\ntotal: %d | errors: %d | err_rate= %.2f%s\n'%(index,errors,float(errors)*100/index,'%'))

		data = pd.DataFrame(scraped_data)
		first_count = len(data.index)
		data.dropna(inplace = True)
		data.drop_duplicates(subset = 'title',inplace=True)
		second_count = len(data.index)
		
		print('removing duplicates: before= %d | after= %d\n'%(first_count,second_count))
		
		if output_csv:
			data.to_csv(self.config['REUTERS']['OutputPath_World'],encoding = 'utf-8',index = None)
		
		return data