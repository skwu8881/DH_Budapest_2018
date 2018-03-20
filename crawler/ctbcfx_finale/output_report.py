from lib.ctbcfxSQL import ctbcfxSQL
import pandas as pd
import sys
from datetime import datetime

startdate = sys.argv[1]
enddate = sys.argv[2]
targets = ['cnbc_us','forexfactory','forexlive','reuters','zerohedge']
save_cols = ['content','time']

DBconn = ctbcfxSQL()

output_df = pd.DataFrame(columns=save_cols)
output_df['source'] = []
for target in targets:
	raw_data = DBconn.query(cols='*',table=target,condition_str='time < "'+enddate+' 23:59:59" AND time > "'+startdate+' 00:00:00"')
	fomc_news = pd.DataFrame(raw_data)
	fomc_news = fomc_news[save_cols]
	
	source = [ target for _ in range(len(fomc_news))]
		
	for col in save_cols:
		output_df.append(fomc_news[col], ignore_index=True)
	output_df['source'].append(pd.Series(source), ignore_index=True)
	
output_df.to_csv('%s_%s_report.csv'%(startdate,enddate),index=False)