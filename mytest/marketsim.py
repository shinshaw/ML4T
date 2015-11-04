"""MC2-P1: Market simulator."""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
import  QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.qsdateutil as du
from util import get_data, plot_data
from portfolio.analysis import get_portfolio_value, get_portfolio_stats, plot_normalized_data

def compute_portvals(start_date, end_date, orders_file, start_val):
    """Compute daily portfolio value given a sequence of orders in a CSV file.

    Parameters
    ----------
        start_date: first date to track
        end_date: last date to track
        orders_file: CSV file to read orders from
        start_val: total starting cash available

    Returns
    -------
        portvals: portfolio value for each trading day from start_date to end_date (inclusive)
    """
    # TODO: Your code here
    startDate=dt.datetime.strptime(start_date, "%Y-%m-%d")
    endDate=dt.datetime.strptime(end_date, "%Y-%m-%d")
    symbols=set()
    df_orders=pd.read_csv(orders_file)
    dates=pd.date_range(startDate,endDate)
    df_price=pd.DataFrame(index=dates)

    num=len(df_orders['Symbol'])

    for symbol in df_orders['Symbol']:
         symbols.add(symbol)

    for symbol in symbols:
         df_temp=pd.read_csv("data/{}.csv".format(symbol),index_col='Date',parse_dates=True,usecols=['Date','Adj Close'],na_values=['nan'])
         df_temp=df_temp.rename(columns={'Adj Close':symbol})
         df_price=df_price.join(df_temp)
         df_price=df_price.fillna(method="ffill")

    df_trade = pd.DataFrame(index=dates, columns=symbols)
    df_trade= df_trade.fillna(0)
    for i in range(num):
        df_orders['Date'][i]=dt.datetime.strptime(df_orders['Date'][i],"%Y-%m-%d")
        for d in dates:
            if d==df_orders['Date'][i]:
                symbol=df_orders['Symbol'][i]
                if df_orders['Order'][i]=="BUY":
                    df_trade[symbol][d]=df_trade[symbol][d]+int(df_orders['Shares'][i])
                elif df_orders['Order'][i]=="SELL":
                    df_trade[symbol][d]=df_trade[symbol][d]-int(df_orders['Shares'][i])

    df_trade_abs=abs(df_trade)

    df_holding = pd.DataFrame(index=dates, columns=symbols)
    df_holding= df_holding.fillna(0)
    for s in symbols:
        df_holding[s][dates[0]]=df_trade[s][dates[0]]
        for i in range(1,len(dates)):
            df_holding[s][dates[i]]=df_trade[s][dates[i]]+df_holding[s][dates[i-1]]


    df_holding_value=df_holding*df_price

    df_holding_value=df_holding_value.dropna()
    df_total_holding=df_holding_value.sum(axis=1)

    column=['cash']
    df_value=pd.DataFrame(index=dates)
    df_value=df_trade*df_price
    df_value_abs=df_trade_abs*df_price
    df_value_abs_total=df_value_abs.sum(axis=1)
    df_use_abs=pd.DataFrame(index=dates, columns=column)
    df_use_abs=df_use_abs.fillna(0.00)
    df_temp1=df_value_abs.sum(axis=1)
    for d in dates:
        df_use_abs['cash'][d]=df_temp1[d]

    df_use=pd.DataFrame(index=dates, columns=column)
    df_use=df_use.fillna(0.00)
    df_temp2=df_value.sum(axis=1)
    for d in dates:
        df_use['cash'][d]=df_temp2[d]

    column=['cash']
    df_cash=pd.DataFrame(index=dates, columns=column)

    df_cash=df_cash.fillna(0.00)

    df_cash['cash'][dates[0]]=start_val-df_use['cash'][dates[0]]


    for i in range(1,len(dates)):
        df_cash['cash'][dates[i]]=df_cash['cash'][dates[i-1]]-df_use['cash'][dates[i]]


    timestamps = du.getNYSEdays(startDate, endDate, dt.timedelta(hours=0))
    df_portval=df_total_holding + df_cash

    portvals=pd.DataFrame(index=timestamps)
    portvals=portvals.join(df_portval)


    return portvals



def test_run():
    """Driver function."""
    # Define input parameters
    start_date = '2014-06-26'
    end_date = '2015-11-03'
    orders_file = os.path.join("orders", "myorder_.csv")
    start_val = 10000

    # Process orders
    portvals = compute_portvals(start_date, end_date, orders_file, start_val)
    print portvals['2015-08-10':'2015-10-10']
    portvals_order=portvals/portvals.ix[0]

    portvals_order=portvals_order.rename(columns={"cash":'Portfolio'})

    ax=portvals_order.plot(title="Daily Portfolio Value",label='Portfolio',color='g')


    if isinstance(portvals, pd.DataFrame):
        portvals = portvals[portvals.columns[0]]

    cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio = get_portfolio_stats(portvals)
    dates=pd.date_range(start_date, end_date)
    df_SPY = pd.DataFrame(index=dates)
    df_temp = pd.read_csv("data/SPY.csv", index_col='Date',
                parse_dates=True, usecols=['Date', 'Adj Close'], na_values=['nan'])
    df_temp = df_temp.rename(columns={'Adj Close': 'SPY'})
    df_SPY = df_SPY.join(df_temp)
    df_SPY = df_SPY.dropna(subset=["SPY"])
    df_SPY = df_SPY[['SPY']]
    portvals_SPY = get_portfolio_value(df_SPY, [1.0])
    portvals_SPY.plot(label='SPY',ax=ax,color='r')
    ax.legend(loc='lower left')


    cum_ret_SPY, avg_daily_ret_SPY, std_daily_ret_SPY, sharpe_ratio_SPY = get_portfolio_stats(portvals_SPY)

    print "Data Range: {} to {}".format(start_date, end_date)
    print
    print "Sharpe Ratio of Fund: {}".format(sharpe_ratio)
    print "Sharpe Ratio of SPY: {}".format(sharpe_ratio_SPY)
    print
    print "Cumulative Return of Fund: {}".format(cum_ret)
    print "Cumulative Return of SPY: {}".format(cum_ret_SPY)
    print
    print "Standard Deviation of Fund: {}".format(std_daily_ret)
    print "Standard Deviation of SPY: {}".format(std_daily_ret_SPY)
    print
    print "Average Daily Return of Fund: {}".format(avg_daily_ret)
    print "Average Daily Return of SPY: {}".format(avg_daily_ret_SPY)
    print
    print "Final Portfolio Value: {}".format(portvals[-1])

    plt.show()

if __name__ == "__main__":
    test_run()
