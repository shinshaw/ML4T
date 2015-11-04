
__author__ = 'shinshaw'
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt


def symbol_to_path(symbol, base_dir="data"):
    return os.path.join(base_dir, "{}.csv".format(str(symbol)))

def get_data(symbols,dates):
    df=pd.DataFrame(index=dates)
    for symbol in symbols:
        df_temp = pd.read_csv(symbol_to_path(symbol), index_col='Date',
                parse_dates=True, usecols=['Date', 'Adj Close'], na_values=['nan'])
        df_temp = df_temp.rename(columns={'Adj Close': symbol})
        df = df.join(df_temp)
    df=df.dropna()
    return df

def get_data_all(symbols,dates):
    df=pd.DataFrame(index=dates)
    for symbol in symbols:
        df_temp = pd.read_csv(symbol_to_path(symbol), index_col='Date',
                parse_dates=True,  na_values=['nan'])

        df = df.join(df_temp)
    df=df.dropna()
    return df

def plot_data(df,title="Stock prices"):
    ax=df.plot(title=title,fontsize=12)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    plt.show()

def get_rolling_mean(values, window):
    return pd.rolling_mean(values, window=window)



def write():
    name='myorder_.csv'
    try:
        file1 = open(name,'a')
        file1.write('Date'+',')
        file1.write('Symbol'+',')
        file1.write('Order'+',')
        file1.write('Shares')
        file1.close()
    except:
        print('Something went wrong!')
        sys.exit(0)


def order(df,rsi,symbol,sma_12,sma_26,ax,index):
    for d in df.index[index:]:
        t_entry=pd.Timestamp(d)
        loc_entry=df.index.get_loc(t_entry)
        ymin, ymax = ax.get_ylim()

        if sma_12.iloc[loc_entry]>sma_26.iloc[loc_entry] and sma_12.iloc[loc_entry-1]<sma_26.iloc[loc_entry-1] or rsi.iloc[loc_entry]>60:

            ax.vlines(x=d, ymin=ymin, ymax=ymax-1,color='g')
            loc_entry=loc_entry
            f=open('myorder_.csv','ab+')
            d=d.date()
            date=str(d)
            f.write('\n'+date+',')
            f.write(symbol+',')
            f.write('BUY'+',')
            f.write('100')
            for d1 in df.index[loc_entry+1:]:
                t_exit=pd.Timestamp(d1)
                loc_exit=df.index.get_loc(t_exit)
                if sma_12.iloc[loc_exit]<sma_26.iloc[loc_exit] and sma_12.iloc[loc_exit-1]>sma_26.iloc[loc_exit-1] and rsi.iloc[loc_exit]<50:
                    ax.vlines(x=d1, ymin=ymin, ymax=ymax-1,color='k')
                    f=open('myorder_.csv','ab+')
                    d1=d1.date()
                    date=str(d1)
                    f.write('\n'+date+',')
                    f.write(symbol+',')
                    f.write("SELL"+',')
                    f.write("100")
                    order(df,rsi,symbol,sma_12,sma_26,ax,loc_exit)
                    break
            break


        if sma_12.iloc[loc_entry]<sma_26.iloc[loc_entry] and sma_12.iloc[loc_entry-1]>sma_26.iloc[loc_entry-1] and rsi.iloc[loc_entry]<40:
            ax.vlines(x=d, ymin=ymin, ymax=ymax-1,color='r')
            f=open('myorder_.csv','ab+')
            d=d.date()
            date=str(d)
            f.write('\n'+date+",")
            f.write(symbol+",")
            f.write("SELL"+",")
            f.write("100")
            for d1 in df.index[loc_entry+1:]:
                t_exit=pd.Timestamp(d1)
                loc_exit=df.index.get_loc(t_exit)
                if sma_12.iloc[loc_exit]>sma_26.iloc[loc_exit] and sma_12.iloc[loc_exit-1]<sma_26.iloc[loc_exit-1] or rsi.iloc[loc_exit]>70:
                    ax.vlines(x=d1, ymin=ymin, ymax=ymax-1,color='k')
                    f=open('myorder_.csv','ab+')
                    d1=d1.date()
                    date=str(d1)
                    f.write('\n'+date+',')
                    f.write(symbol+','   )
                    f.write('BUY'+',')
                    f.write('100')
                    order(df,rsi,symbol,sma_12,sma_26,ax,loc_exit)
                    break
            break

def RSI(df, n):
    i = 0
    UpI = [0]
    DoI = [0]
    while i + 1 <= df.index[-1]:
        UpMove = df.get_value(i + 1, 'High') - df.get_value(i, 'High')
        DoMove = df.get_value(i, 'Low') - df.get_value(i + 1, 'Low')
        if UpMove > DoMove and UpMove > 0:
            UpD = UpMove
        else: UpD = 0
        UpI.append(UpD)
        if DoMove > UpMove and DoMove > 0:
            DoD = DoMove
        else: DoD = 0
        DoI.append(DoD)
        i = i + 1
    UpI = pd.Series(UpI)
    DoI = pd.Series(DoI)
    PosDI = pd.Series(pd.ewma(UpI, span = n, min_periods = n - 1))
    NegDI = pd.Series(pd.ewma(DoI, span = n, min_periods = n - 1))
    RS = pd.Series((PosDI+NegDI) / NegDI, name = 'RSI_' + str(n))
    RSI=100-(100/RS)
    return RSI

def test_run():
    dates=pd.date_range('2013-06-26','2015-11-03')
    symbols=['GRPN']
    symbol='GRPN'
    df=get_data(symbols,dates)
    df_all=get_data_all(symbols,dates)
    df1_all=df_all.reset_index()
    rsi_temp=RSI(df1_all,14)
    rsi=df_all['Adj Close']
    i=0
    for d in rsi.index:
        rsi[d]=rsi_temp[i]
        i+=1
        if i>505:
            break

    ema_12 = get_rolling_mean(df[symbol], window=12)
    ema_26 = get_rolling_mean(df[symbol], window=26)
    ax = df[symbol].plot(title="EMA_12 EMA_26 and RSI", label=symbol)

    ema_12.plot(label='EMA_12', ax=ax,color='m')
    ema_26.plot(label='EMA_26', ax=ax,color='g')
    write()
    order(df,rsi,symbol,ema_12,ema_26,ax, 0)


    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc='lower left')


    plt.show()




if __name__ == "__main__":
    test_run()
