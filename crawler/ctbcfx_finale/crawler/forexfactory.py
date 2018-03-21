from collections import OrderedDict								
import pandas as pd								
from pyquery import PyQuery as pq								
import configparser
import sys, os
import pytz
from datetime import datetime,timedelta

class Forexfactory_Crawler:								
	def __init__(self, startpage=None, stoppage=None):
		#initialize paths and constants
		#conf = os.path.abspath(os.path.join(sys.path[0], os.pardir))
		self.config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
		#self.config.read(conf + '/config.ini')
		self.config.read(sys.path[0] + '/config.ini')
		
		t = pq(self.config['FOREXFACTORY']['QueryURL'])
		self.curr_lastpage = int(t('a.last').text()[0:4]) #getmaxpage alternatively...QQ
		
		if startpage == None and stoppage == None:
			self.stoppage = self.curr_lastpage
			self.startpage = self.stoppage - 5
		elif stoppage == None:
			self.stoppage = self.curr_lastpage
		elif startpage == None:
			self.stoppage = stoppage
			self.startpage = int(self.config['FOREXFACTORY']['FirstPage'])
		else:
			self.startpage = startpage
			self.stoppage = stoppage
		
		self.list1 = []						
		self.list2 = []						
		self.org_url = self.config['FOREXFACTORY']['QueryURL']					
		self.num = self.config['FOREXFACTORY']['FirstPage']
		
		
	def detectmaxpages(self):
		oldtext = ''						
		while True:						
			q = pq(self.org_url + '&page=' + str(self.num))					
			contents = q('div.threadpost-content')					
			detect_q = pq(contents[0])					
			text = detect_q('div.threadpost-content__message').text()					
			if text != oldtext:					
				self.num += 1				
				oldtext = text				
			else:					
				print('=== The last page is:', self.num - 1, '===')				
				break				
								
			print('... Detecting', self.num, 'th page ...')
	
	def getmaxpage(self):
		print("Current LastPage is: %d ."%(self.curr_lastpage));
		return self.curr_lastpage
								
	def execute(self, output_csv=True):
		self.getmaxpage()
	
		for i in range(self.startpage, self.stoppage + 1):						
			tmp_content = []					
			tmp_time = []					
			tmp_title = []					
								
			if i == 1:					
				url = self.org_url				
			else:					
				url = self.org_url + "&page=" + str(i)				
								
			q = pq(url)					
								
			contents = q('div.threadpost-content')					
			for each in contents:					
				info_dict = {}				
				eachpost_q = pq(each)				
				text = eachpost_q('div.threadpost-content__message').text()				
				info_dict['content'] = text				
				# print(text)				
				self.list2.append(info_dict)				
								
			titles = q('div.threadpost-header')					
			for each in titles:					
				info_dict = {}				
				eachtitle_q = pq(each)
				utc_time = None
				parse_time_bak = ""
				try:
					parse_time = eachtitle_q('span.visible-dv.visible-tv').text()[5:]
					parse_time = parse_time.split(' (')[0]
					parse_time = parse_time.replace('Post ','')
					parse_time = parse_time.replace('Edited ','')
					parse_time = parse_time.replace('2017 ','')
					parse_time = parse_time.split(' | ')[0]
					parse_time = parse_time.split(' Joined ')[0]
					parse_time = '2017 ' + parse_time
					parse_time_bak = parse_time
					new_parse_time = datetime.strptime(parse_time,'%Y %b %d, %I:%M%p').strftime('%Y-%m-%d %H:%M:%S')
					edt_time = str(pd.to_datetime(new_parse_time))
					us = pytz.timezone('America/New_York')
					dt = datetime.strptime(edt_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=us)
					utc_time = pd.to_datetime(dt.astimezone(pytz.utc))
				except:
					utc_time = "error date: " + parse_time_bak
				info_dict['time'] = str(utc_time)
				
				# print(time)				
								
				# No title (assign to "none")				
				info_dict['title'] = 'none'				
				self.list1.append(info_dict)
			if i%100==0:					
				print('completed:', i)					
								
								
		df1 = pd.DataFrame(self.list1)						
		df2 = pd.DataFrame(self.list2)						
		df = pd.concat([df1, df2],axis = 1)						
		
		if output_csv:
			df.to_csv(self.config['FOREXFACTORY']['OutputPath'],encoding='utf-8',index=None)						
		
		return df