import pandas as pd

bydate = pd.read_csv('/Users/xiechangrun/Desktop/ctbcfx/treemodel/bydate.csv',encoding = 'utf-8')
b2 = bydate.sum(axis = 0).reset_index()
b2.columns = [['ea','freq']]
b2 = b2.loc[2:,:]
b2.freq = b2.freq.astype(int) 
b2 = b2.query('freq >= 30')
a_list = []
for each in b2.ea:
    a_list.append(each)
b3 = bydate[['commodity@bad', 'commodity@down', 'commodity@good', 'commodity@up', 'econ@bad', 'econ@good', 'econ@up', 'employ@good', 'employ@up', 'rate@bad', 'rate@down', 'rate@good', 'rate@low', 'rate@up', 'treasury@good', 'yeild@down', 'yeild@up']]

def b3_transform(x):
    if x > 0:
        return 1
    else:
        return 0 

b4 = b3.copy()
for col in b3.columns:
    b4[col] = b3[col].apply(b3_transform)
    
b4 = pd.concat([bydate['time'],b4],axis = 1)
b4['time'] = pd.to_datetime(b4['time'])

jpy = pd.read_csv('/Users/xiechangrun/Desktop/USDJPY.csv',encoding = 'utf-8')
jpy2 = jpy[(pd.to_datetime(jpy.Date) >= pd.to_datetime('2015-01-31')) & (pd.to_datetime(jpy.Date) <= pd.to_datetime('2015-08-01'))]
jpy2['diff'] = (jpy2['PX_LAST'] - jpy2['PX_LAST'].shift()) /jpy2['PX_LAST'].shift()
def jpylabel(x):
    if x >= 0.001:
        return 1
    if x <= -0.001:
        return -1
    else:
        return 0

jpy2['label'] = jpy2['diff'].apply(jpylabel)
jpy2.groupby('label').count()
jpy2.rename(columns={'Date':'time'}, inplace=True)
jpy_merge = jpy2[['label','time']]
jpy_merge['time'] = pd.to_datetime(jpy_merge['time'])
jpy_merge.reset_index(inplace=True,drop = True)

arule = pd.merge(b4,jpy_merge,on='time',how='outer')

try:
    del arule['time']
except:
    pass

arule.dropna(inplace=True)
arule.to_csv('/Users/xiechangrun/Desktop/arule4.csv',encoding = 'utf-8',index=None)