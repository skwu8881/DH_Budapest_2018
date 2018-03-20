import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY
from matplotlib.finance import candlestick_ohlc
from matplotlib import style
from datetime import datetime
import numpy as np
import pandas as pd

class showResults():
    def __init__(self, forex_df, hold, window):
        self.hold = hold
        self.df = forex_df
        self.window = window

    def plot_result(self, pl_result, placc_result):
        
        forex_df = self.df

        list2 = []
        # convert time format to "proleptic Gregorian ordinal, where January 1 of year 1 has ordinal 1" ,
        # which is necessary for matplotlib.finance.
        forex_date = list(forex_df['time'])
        forex_date = [datetime.strftime(d,'%Y-%m-%d') for d in forex_date]
        forex_date = [datetime.strptime(d,'%Y-%m-%d') for d in forex_date]
        forex_date = [d.toordinal() for d in forex_date]

        forex_price = list(forex_df['jpus_price'])
        enter_action = list(forex_df['label'])

        enterIdBuy = list(np.array(forex_date)[np.array(enter_action) == 1])
        enterIdSell = list(np.array(forex_date)[np.array(enter_action) == -1])
        enterPriceBuy = list(np.array(forex_price)[np.array(enter_action) == 1])
        enterPriceSell = list(np.array(forex_price)[np.array(enter_action) == -1])

        out_action = [np.nan for i in range(self.hold+1)] + list(forex_df['label'] * (-1))
        # create input format for matplotlib.finance.
        for i in range(len(forex_price)):
            openprice = forex_price[i] 
            #enterprice = forex_price[i] + enter_action[i]
            outprice = forex_price[i] + out_action[i]
            date = forex_date[i]
            list2.append((date, openprice, openprice, outprice, outprice, 0))

        # plot the result by matplotlib.finance.
        # mondays = WeekdayLocator(MONDAY)         # major ticks on the mondays
        alldays = DayLocator()                   # minor ticks on the days
        weekFormatter = DateFormatter('%y %b %d')   # e.g., Jan 12
        dayFormatter = DateFormatter('%d')       # e.g., 12
        
        ax1 = plt.subplot2grid((6,1), (0,0), rowspan=4, colspan=1)
        ax2 = plt.subplot2grid((6,1), (4,0), rowspan=2, colspan=1, sharex=ax1)

        # fig, ax = plt.subplots()
        # fig.subplots_adjust(bottom=0.2)
        # ax1.xaxis.set_major_locator(mondays)
        ax1.xaxis.set_minor_locator(alldays)
        ax1.xaxis.set_major_formatter(weekFormatter)

        candlestick_ohlc(ax1, list2, width=0.4, colorup='#77d879', colordown='#db3f3f')
        ax1.scatter(enterIdBuy, enterPriceBuy, marker='x', c='green')
        ax1.scatter(enterIdSell, enterPriceSell, marker='x', c='red')
        ax1.plot(forex_date, forex_price, color='#828b8c', alpha=0.8)
        ax1.xaxis_date()
        ax1.autoscale_view()
        plt.setp(ax1.get_xticklabels(), visible=False)

        ax2.plot(forex_date, placc_result, color='red', label='Accum P/L')
        plt.legend()
        # make double y-axis in same plot
        ax3 = ax2.twinx() 
        ax3.plot(forex_date, pl_result, label='P/L')
        
        plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
        plt.legend()
        plt.show()
        
    def PL_SR(self):
        
        df = self.df
        hold = self.hold
        df['pl'] = df['label']*( (df['jpus_price']-df['jpus_price'].shift(hold)) / df['jpus_price'].shift(hold) ) 
        df.to_csv('pl.csv')
        tradingDay = (len(df['pl'].index) - hold - self.window)
        print('trading Days :', tradingDay)
        PL = np.sum(df['pl']) / (tradingDay / 252) * 100
        print('P&L :', PL, '%')
        print('Sharpe ratio :', np.mean(df['pl'])/np.std(df['pl']))

        df['pl_accum'] = df.pl.cumsum()
        pl_result = df['pl'].tolist()
        placc_result = df['pl_accum'].tolist()
        
        return pl_result, placc_result
        
