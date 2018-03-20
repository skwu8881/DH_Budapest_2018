import sys
import os
from lib.ctbcfxSQL import ctbcfxSQL
import pandas as pd
import numpy as np
import pytz
from datetime import datetime,timedelta

DBconn = ctbcfxSQL() #global SQL connection

#========= IMSERT FUNCTIONS =============
def cmod(tablename, filepath):
	print('start inserting file: "%s" to TABLE[%s]...'%(filepath, tablename))
	with open(filepath, 'r',encoding='utf8') as f:
		i = 0
		for line in f:
			if i > 0:
				line = line.replace('\n','').replace('\r', '')
				data1 = str(line).split(',')
				word = data1[0]
				
				data2 = str(data1[1]).split('#')
				entity = data2[0]
				aspect = data2[1]
				
				DBconn.insert('entity',['entity'],[entity])
				DBconn.insert('aspect',['entity','aspect'],[entity,aspect])
				DBconn.insert('word',['aspect','word'],[aspect,word])
				
			i += 1
	
	print('insertion done. removing duplicates...')
	DBconn.rawSQL('DELETE a FROM entity as a, entity as b WHERE a.entity = b.entity AND a.ID < b.ID;')
	DBconn.rawSQL('DELETE a FROM aspect as a, aspect as b WHERE a.aspect = b.aspect AND a.entity = b.entity AND a.ID < b.ID;')
	
	print('\n[complete.]\n')

def cnbc_us(tablename, filepath):
	print('start inserting file: "%s" to TABLE[%s]...'%(filepath, tablename))
	f = pd.read_csv(filepath, encoding = 'utf8', low_memory=False)
	f.dropna(axis=1, how='any', inplace=True, thresh=int(len(f.index)/2))
	f.dropna(axis=0, how='any', inplace=True)
	datas = f.values.tolist()
	for data in datas:
		data[1] = data[1].split('+')[0]
		DBconn.insert(tablename,['title','time','content'],data)

def reuters(tablename, filepath):
	print('start inserting file: "%s" to TABLE[%s]...'%(filepath, tablename))
	f = pd.read_csv(filepath, encoding = 'utf8', low_memory=False)
	f.dropna(axis=1, how='any', inplace=True, thresh=int(len(f.index)/2))
	f.dropna(axis=0, how='any', inplace=True)
	datas = f.values.tolist()
	for data in datas:
		data[1] = data[1].split('+')[0]
		DBconn.insert(tablename,['title','time','content'],data)

def zerohedge(tablename, filepath):
	print('start inserting file: "%s" to TABLE[%s]...'%(filepath, tablename))
	f = pd.read_csv(filepath, encoding = 'utf8', low_memory=False)
	f.dropna(axis=1, how='any', inplace=True, thresh=int(len(f.index)/2))
	f.dropna(axis=0, how='any', inplace=True)
	datas = f.values.tolist()
	for data in datas:
		data[1] = data[1].split('+')[0]
		DBconn.insert(tablename,['title','time','content','tag'],data)
			
def forexlive(tablename, filepath):
	print('start inserting file: "%s" to TABLE[%s]...'%(filepath, tablename))
	f = pd.read_csv(filepath, encoding = 'utf8', low_memory=False)
	f.dropna(axis=1, how='any', inplace=True, thresh=int(len(f.index)/2))
	f.dropna(axis=0, how='any', inplace=True)
	datas = f.values.tolist()
	for data in datas:
		data[0] = data[0].split('+')[0]
		DBconn.insert(tablename,['time','author','title','content'],data)

def forexfactory(tablename, filepath):
	print('start inserting file: "%s" to TABLE[%s]...'%(filepath, tablename))
	f = pd.read_csv(filepath, encoding = 'utf8', low_memory=False)
	f.dropna(axis=1, how='any', inplace=True, thresh=int(len(f.index)/2))
	f.dropna(axis=0, how='any', inplace=True)
	datas = f.values.tolist()
	for data in datas:	
		data[0] = data[0].split('+')[0]
		DBconn.insert(tablename,['time','title','content'],data)

	
def main():
	if len(sys.argv)!=2+1:
		print('\n  *usage: python3',str(sys.argv[0]),'[table_name] [csv_filePath]\n')
		return

	selector = {'cmod':cmod, 'cnbc_us':cnbc_us, 'reuters':reuters,
				'forexlive':forexlive, 'forexfactory':forexfactory, 'zerohedge':zerohedge}
	filepath = sys.argv[2]
	tablename = sys.argv[1]
	
	selector[tablename](tablename, filepath)
	
	print('insertion done. removing duplicates...')
	DBconn.crawler_DelDup(tablename)
	
	print('\n[complete.]\n')
	
	
if __name__ == "__main__":
	main()