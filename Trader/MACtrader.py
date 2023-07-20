import datetime
from binance.client import Client
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scrap import get_historical_data
from dataapi import api_key as data_api, secret_key as data_secret
from testapi import api_key as testnet_api, secret_key as testnet_secret
import sys
import os
sys.path.insert(1, './strategies')
from MACStrategy import MAC
from datetime import datetime


class MACTrader():
    def __init__(self, symbols, params, usdtunits, testnet_client, data_client, bar_length):
        self.symbols = symbols
        self.params_dict = params_dict
        self.usdtunits = usdtunits
        self.testnet_client = testnet_client
        self.data_client = data_client
        self.available_intervals = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d",
                                    "1w", "1M"]
        self.bar_length = bar_length
        self.trades = 0
        self.trade_values = []
        self.price_data = None
        self.position_data = None
        self.last_positions = None
        self.last_positions_path = "./Trader/positions/MAC.csv"

    def get_most_recent(self, interval, days, data_client):
        now = datetime.utcnow()
        past = str(now - timedelta(days=days))
        price_list = []
        for symbol in self.symbols:
            data = get_historical_data(past, now, data_client, symbol, interval)
            data = data.loc["2019-01-01":]
            dataSeries = data["Close"].rename(symbol)
            price_list.append(dataSeries)
        self.price_data = pd.concat(price_list, axis=1)
    def define_strategy(self):
        macStrat = MAC(None, None, self.price_data.copy(), self.symbols)
        for symbol, params in self.params_dict.items():
            macStrat.generate_signals(symbol, params)
        self.position_data = macStrat.position_data

    def execute_trades(self):
        last_positions = pd.read_csv(self.last_positions_path)
        for symbol in self.symbols:
            # current position is long
            price = self.price_data[symbol].iloc[-1]
            unitsToOrder = round(self.usdtunits / price,3)
            if self.position_data[symbol].iloc[-1] == 1:
                # go long
                if self.last_positions[symbol].iloc[-1] == 0:
                    order = testnet_client.create_order(symbol=symbol, side="BUY", type="MARKET", quantity = unitsToOrder)
                    self.report_trade(order, "GOING LONG", symbol)
                else:
                    print(f"{symbol}: Remain Long")
            # current position is neutral
            if self.position_data[symbol].iloc[-1] == 0:
                if self.last_positions[symbol].iloc[-1] == 1:
                    order = testnet_client.create_order(symbol=symbol, side="SELL", type="MARKET", quantity = unitsToOrder)
                    self.report_trade(order, "GOING NEUTRAL")
                else:
                    print(f"{symbol}: Remain Neutral")
        self.last_positions = self.position_data.tail(1)
        self.last_positions.to_csv("./Trader/positions/MAC.csv")

    def start_trading(self):
        # last positions are all zero
        if not os.path.isfile(trader.last_positions_path):
            last_positions = pd.DataFrame(data=0, index=[datetime.utcnow().date()], columns=self.symbols)
            last_positions.to_csv("./Trader/positions/MAC.csv")
            self.last_positions = last_positions
        # last position are being tracked
        else:
            self.last_positions = pd.read_csv(self.last_positions_path)
        trader.get_most_recent(bar_length, 200, data_client)
        trader.define_strategy()
        trader.execute_trades()

    def report_trade(self, order, going, symbol):

        # extract data from order object
        side = order["side"]
        time = pd.to_datetime(order["transactTime"], unit="ms")
        base_units = float(order["executedQty"])
        quote_units = float(order["cummulativeQuoteQty"])
        price = round(quote_units / base_units, 5)

        # calculate trading profits
        self.trades += 1
        if side == "BUY":
            self.trade_values.append(-quote_units)
        elif side == "SELL":
            self.trade_values.append(quote_units)

        if self.trades % 2 == 0:
            real_profit = round(np.sum(self.trade_values[-2:]), 3)
            self.cum_profits = round(np.sum(self.trade_values), 3)
        else:
            real_profit = 0
            self.cum_profits = round(np.sum(self.trade_values[:-1]), 3)

        # print trade report
        print(2 * "\n" + 100 * "-")
        print("{} | {} | {}".format(time, going, symbol))
        print("{} | Base_Units = {} | Quote_Units = {} | Price = {} ".format(time, base_units, quote_units, price))
        print("{} | Profit = {} | CumProfits = {} ".format(time, real_profit, self.cum_profits))
        print(100 * "-" + "\n")


if __name__ == "__main__":  # only if we run MACtrader.py as a script, please do the following:
    testnet_client = Client(api_key=testnet_api, api_secret=testnet_secret, tld="com", testnet=True)
    data_client = Client(api_key=data_api, api_secret=data_secret, tld="com")
    symbols = ["BTCUSDT", "ETHUSDT"]
    params_dict = {'BTCUSDT': (10.0, 25.0), 'ETHUSDT': (15.0, 50.0)}
    bar_length = "1d"
    units = 50 # e.g each trade use 50 usdt
    trader = MACTrader(symbols=symbols, params = params_dict, usdtunits=units, testnet_client=testnet_client, data_client = data_client, bar_length = "1d")
    trader.start_trading()
    print(testnet_client.get_account())