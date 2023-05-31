import os
from binance.client import Client
from binance import ThreadedWebsocketManager
import pprint
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import threading




TEST_NET = True

 
def get_data_frame():
    starttime = '1 day ago UTC'
    interval = '5m'
    bars = client.get_historical_klines(symbol, interval, starttime)
    
    for line in bars:                #keep only first 5 colums date,open,high,low,close
        del line[5:]

    df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close']) 
    return df  

def plot_graph(df):

    df=df.astype(float)
    df[['close', 'MACD', 'signal']].plot()
    plt.xlabel('Date',fontsize=18)
    plt.ylabel('Close price',fontsize=18)
    x_axis = df.index

    plt.scatter(df.index,df['Buy'],color='purple',label='Buy', marker= '^', alpha=1)
    plt.scatter(df.index,df['Sell'],color='red',label='Sell', marker= 'v', alpha=1)

    plt.show()    




def buy_or_sell(df, buy_sell_list, stop_loss_list, symbol, client):
    for index, value in enumerate(buy_sell_list):
        current_price = client.get_symbol_ticker(symbol =symbol)
        print(current_price['price'])
        if value == 1.0: #signal to buy
            if current_price['price'] < df['Buy'][index]:
                print("buy buy buy.....")
                buy_order = client.order_market_buy(symbol=symbol, quantity=1)
                print(buy_order)
        elif value == -1.0: #signal to sell
            if float(current_price['price']) > float(df['Sell'][index]) or float(current_price['price']) <= float(df['Stop'][index]):
                print("sell sell sell....")
                sell_order = client.order_market_sell(symbol=symbol, quantity=1)
                print(sell_order)           
        else:
            print("nothing to do.....")

def get_trade(row):
    if row['Buy'] == row['Buy']:
        return "Buy"
    elif row['Sell'] == row['Sell']:
        return "Sell"
    else:
        return "None"




def macd_trade_logic():
    symbol_df = get_data_frame()

    # calculate short and long ema mostly using close values
    shortEMA = symbol_df['close'].ewm(span=12, adjust=False).mean()
    longEMA = symbol_df['close'].ewm(span=26, adjust=False).mean()

    #calculate MACD and signal line
    MACD = shortEMA - longEMA
    signal = MACD.ewm(span=9, adjust=False).mean()

    symbol_df['MACD'] = MACD
    symbol_df['signal'] = signal

    #to print in human readable date and time(form timestamp)
    symbol_df.set_index('date', inplace=True)
    symbol_df.index = pd.to_datetime(symbol_df.index, unit='ms') #index set to firts column = date_and_time
    
    symbol_df['Trigger'] = np.where(symbol_df['MACD'] > symbol_df['signal'], 1,0)
    symbol_df['Position'] = symbol_df['Trigger'].diff()
    
  

    #add buy and sell columns
    symbol_df['Buy'] = np.where(symbol_df['Position'] == 1,symbol_df['close'], np.NaN)
    symbol_df['Sell'] = np.where(symbol_df['Position'] == -1,symbol_df['close'], np.NaN)
    # Convert the 'close' column to a numeric type and replace any 'NaN' values with 0
    symbol_df['close'] = pd.to_numeric(symbol_df['close'], errors='coerce').fillna(0)
    # Multiply the 'close' column by 0.95 and assign the result to a new column called 'Stop'
    symbol_df['Stop'] = symbol_df['close'] * 0.95
    # Add a 'Trades Executed' column to the DataFrame
    symbol_df['Trades Executed'] = symbol_df.apply(get_trade, axis=1)
    


    with open('ttx.1', 'w') as f:
        f.write(
            symbol_df.to_string()
        )                                                                                                                                                                                                                                                                                  
       # plot_graph(symbol_df)
   

    buy_sell_list = symbol_df['Position'].tolist()
    stop_loss_list = symbol_df['Position'].tolist()

    buy_or_sell(symbol_df, buy_sell_list, stop_loss_list, symbol, client)




def main():
    macd_trade_logic()  


if __name__ == "__main__":
    if TEST_NET:
        api_key = 'vKQHFKr4JwUe42fzFMbZ75d1ZsFRaciHGceSi1la8wsmpRmsi58wG6xGbErck8s5'
        api_secret = '8YiY4kgyvibyfL5IHdzdodmoKRagApU4V27V2boaE1HeFI4v2i3W1cd1CzfKoZaj'

        client = Client(api_key, api_secret, testnet=True)
        print("using Binance Testnet server")

   
    pprint.pprint(client.get_account())
    
    symbol='BNBUSDT'
    main()

