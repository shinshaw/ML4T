
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

def plot_data(df,title="Stock prices"):
    ax=df.plot(title=title,fontsize=12)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    plt.show()

def get_rolling_mean(values, window):
    return pd.rolling_mean(values, window=window)

def get_rolling_std(values, window):
    return pd.rolling_std(values,window=window)

def get_bollinger_bands(rm, rstd):
    upper_band=rm+rstd*2
    lower_band=rm-rstd*2
    return upper_band, lower_band

def write():
    name='myorder.txt'
    try:
        file1 = open(name,'a')
        file1.write('Date              ')
        file1.write('  Symbol   ')
        file1.write('Order   ')
        file1.write('Shares   ')
        file1.close()
    except:
        print('Something went wrong!')
        sys.exit(0)


def order(df,symbol,lower_band,upper_band,sma,ax,index):
    for d in df.index[index:]:
        t_entry=pd.Timestamp(d)
        loc_entry=df.index.get_loc(t_entry)
        ymin, ymax = ax.get_ylim()

        if df[symbol].iloc[loc_entry]>lower_band.iloc[loc_entry] and df[symbol].iloc[loc_entry-1]<lower_band.iloc[loc_entry-1]:

            ax.vlines(x=d, ymin=ymin, ymax=ymax-1,color='g')
            loc_entry=loc_entry
            f=open('myorder.txt','ab+')
            d=d.date()
            date=str(d)
            f.write('\n'+date)
            f.write("          "+symbol+"   ")
            f.write("  BUY   ")
            f.write("   100   ")
            for d1 in df.index[loc_entry+1:]:
                t_exit=pd.Timestamp(d1)
                loc_exit=df.index.get_loc(t_exit)
                if df[symbol].iloc[loc_exit]>sma.iloc[loc_exit] and df[symbol].iloc[loc_exit-1]<sma.iloc[loc_exit-1]:
                    ax.vlines(x=d1, ymin=ymin, ymax=ymax-1,color='k')
                    f=open('myorder.txt','ab+')
                    d1=d1.date()
                    date=str(d1)
                    f.write('\n'+date)
                    f.write("          "+symbol+"   ")
                    f.write("  SELL   ")
                    f.write("  100   ")
                    order(df,symbol,lower_band,upper_band,sma,ax,loc_exit)
                    break
            break

        if df[symbol].iloc[loc_entry]<upper_band.iloc[loc_entry] and df[symbol].iloc[loc_entry-1]>upper_band.iloc[loc_entry-1]:
            ax.vlines(x=d, ymin=ymin, ymax=ymax-1,color='r')
            f=open('myorder.txt','ab+')
            d=d.date()
            date=str(d)
            f.write('\n'+date)
            f.write("          "+symbol+"   ")
            f.write("  SELL   ")
            f.write("  100   ")
            for d1 in df.index[loc_entry+1:]:
                t_exit=pd.Timestamp(d1)
                loc_exit=df.index.get_loc(t_exit)
                if df[symbol].iloc[loc_exit]<sma.iloc[loc_exit] and df[symbol].iloc[loc_exit-1]>sma.iloc[loc_exit-1]:
                    ax.vlines(x=d1, ymin=ymin, ymax=ymax-1,color='k')
                    f=open('myorder.txt','ab+')
                    d1=d1.date()
                    date=str(d1)
                    f.write('\n'+date)
                    f.write("          "+symbol+"   "   )
                    f.write("  BUY   ")
                    f.write("   100   ")
                    order(df,symbol,lower_band,upper_band,sma,ax,loc_exit)
                    break
            break


def test_run():
    dates=pd.date_range('2014-06-26','2015-11-02')
    symbols=['AAPL']
    symbol='AAPL'
    df=get_data(symbols,dates)

    sma = get_rolling_mean(df[symbol], window=20)
    rstd = get_rolling_std(df[symbol], window=20)
    upper_band, lower_band = get_bollinger_bands(sma, rstd)

    ax = df[symbol].plot(title="Bollinger Bands", label='IBM')
    sma.plot(label='SMA', ax=ax,color='y')
    upper_band.plot(label='Bollinger upper band', ax=ax,color='m')
    lower_band.plot(label='Bollinger lower band', ax=ax,color='m')

    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc='lower left')
    write()
    order(df,symbol,lower_band,upper_band,sma,ax,0)

    plt.show()




if __name__ == "__main__":
    test_run()
