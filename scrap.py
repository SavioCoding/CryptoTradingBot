from binance.client import Client
from dataapi import api_key, secret_key
import pandas as pd
import datetime

'''
function to get historical data and return the dataframe
'''
def get_historical_data (start_time, end_time, data_client, symbol="BTCUSDT", interval="1d"):
    bars = data_client.get_historical_klines(symbol=symbol, interval=interval, start_str=str(start_time), end_str=str(end_time))
    df = pd.DataFrame(bars)
    df["Date"] = pd.to_datetime(df.iloc[:,0], unit = "ms")
    df.columns = ["Open Time", "Open", "High", "Low", "Close", "Volume", "Close Time", "Quote Asset Volume", "Number of Trades", "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore", "Date"]
    df.set_index("Date", inplace=True)
    for column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    return df

if __name__ == '__main__':

    # Define symbols needed
    symbols = ["BTCUSDT", "ETHUSDT","XRPUSDT"]
    intervals = ["1d", "1h"]
    # Define intervals here
    # intervals allowed ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h",
    # "1d", "3d", "1w", "1M"]


    data_client = Client(api_key = api_key, api_secret = secret_key, tld = "com")
    for i in range(len(symbols)):
        for j in range(len(intervals)):
            symbol = symbols[i]
            interval = intervals[j]
            start = pd.to_datetime(data_client._get_earliest_valid_timestamp(symbol=symbol, interval=interval), unit="ms")
            end = datetime.datetime.utcnow()
            data = get_historical_data(start, end, data_client, symbol, interval)
            data.to_csv("./data/" + symbol + "-" + interval + ".csv")



