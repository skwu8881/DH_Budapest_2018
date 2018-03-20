from crawler.cnbc_us import CNBC_Crawler
from crawler.forexfactory import Forexfactory_Crawler
from crawler.forexlive import Forexlive_Crawler
from crawler.reuters_market import ReutersMarket_Crawler
from crawler.reuters_world import ReutersWorld_Crawler
from crawler.zerohedge import Zerohedge_Crawler
from lib.ctbcfxSQL import ctbcfxSQL
import time
from datetime import datetime, timedelta

def main():
	#initialize utilities
	print('[start mission!]\n--------------------------------')
	startTime = time.time()
	DBconn = ctbcfxSQL()

	#start crawlers & insert databases
	print('source: CNBC | crawler activated.')
	df = CNBC_Crawler(stoppage=25).execute()
	print('complete!')
	df.dropna(axis=1, how='any', inplace=True, thresh=int(len(df.index)/2))
	df.dropna(axis=0, how='any', inplace=True)
	dflist = df.values.tolist()
	print('Data inserting into MySQL (amount=%d)'%(len(dflist)),end="...")
	for d in dflist:
		d[1] = str(d[1]).split('+')[0]
		DBconn.insert('cnbc_us',['title','time','content'],d)
	print('complete!')

	print('source: Forex factory | crawler activated.')
	df = Forexfactory_Crawler().execute()
	print('complete!')
	df.dropna(axis=1, how='any', inplace=True, thresh=int(len(df.index)/2))
	df.dropna(axis=0, how='any', inplace=True)
	dflist = df.values.tolist()
	print('Data inserting into MySQL (amount=%d)'%(len(dflist)),end="...")
	for d in dflist:
		d[0] = str(d[0]).split('+')[0]
		DBconn.insert('forexfactory',['time','title','content'],d)
	print('complete!')

	print('source: Forex Live | crawler activated.')
	df = Forexlive_Crawler(stoppage=50).execute()
	print('complete!')
	df.dropna(axis=1, how='any', inplace=True, thresh=int(len(df.index)/2))
	df.dropna(axis=0, how='any', inplace=True)
	dflist = df.values.tolist()
	print('Data inserting into MySQL (amount=%d)'%(len(dflist)),end="...")
	for d in dflist:
		d[0] = str(d[0]).split('+')[0]
		DBconn.insert('forexlive',['time','author','title','content'],d)
	print('complete!')

	print('source: Reuters Market | crawler activated.')
	df = ReutersMarket_Crawler(stoppage=50).execute()
	print('complete!')
	df.dropna(axis=1, how='any', inplace=True, thresh=int(len(df.index)/2))
	df.dropna(axis=0, how='any', inplace=True)
	dflist = df.values.tolist()
	print('Data inserting into MySQL (amount=%d)'%(len(dflist)),end="...")
	for d in dflist:
		d[1] = str(d[1]).split('+')[0]
		DBconn.insert('reuters',['title','time','content'],d)
	print('complete!')

	print('source: Reuters World | crawler activated.')
	df = ReutersWorld_Crawler(stoppage=50).execute()
	print('complete!')
	df.dropna(axis=1, how='any', inplace=True, thresh=int(len(df.index)/2))
	df.dropna(axis=0, how='any', inplace=True)
	dflist = df.values.tolist()
	print('Data inserting into MySQL (amount=%d)'%(len(dflist)),end="...")
	for d in dflist:
		d[1] = str(d[1]).split('+')[0]
		DBconn.insert('reuters',['title','time','content'],d)
	print('complete!')

	print('source: Zerohedge | crawler activated.')
	df = Zerohedge_Crawler(stoppage=25).execute()
	print('complete!')
	df.dropna(axis=1, how='any', inplace=True, thresh=int(len(df.index)/2))
	df.dropna(axis=0, how='any', inplace=True)
	dflist = df.values.tolist()
	print('Data inserting into MySQL (amount=%d)'%(len(dflist)),end="...")
	for d in dflist:
		d[1] = str(d[1]).split('+')[0]
		DBconn.insert('zerohedge',['title','time','content','tag'],d)
	print('complete!')

	#delete duplicates
	print('start deleting duplicates:\nCNBC running',end="...")
	DBconn.crawler_DelDup('cnbc_us')
	print('DONE!\nForex Factory running',end="...")
	DBconn.crawler_DelDup('forexfactory')
	print('DONE!\nForex Live running',end="...")
	DBconn.crawler_DelDup('forexlive')
	print('DONE!\nReuters running',end="...")
	DBconn.crawler_DelDup('reuters')
	print('DONE!\nZerohedge running',end="...")
	DBconn.crawler_DelDup('zerohedge')
	print('DONE!')

	#process end & evaluate time consumed
	endTime = time.time()
	elapsed = endTime - startTime
	print('------------------------\ntime elapsed: %dm %.1fs'%(int(elapsed/60),(elapsed%60.0)))
	
	print('[endTime="%s"]\n'%(time.ctime()))
	
if __name__=="__main__":
	srt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	print('[startTime="%s"]'%(srt))
	main()
	
	nxt = (datetime.now() + timedelta(minutes = 60)).strftime("%Y-%m-%d %H:%M:%S")
	print('*next job will start at "%s"\n(... sleep 15 min.)\n'%(nxt))
	time.sleep(60.0*60.0)
		