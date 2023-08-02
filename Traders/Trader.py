import datetime
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scrap import get_historical_data
from abc import abstractmethod
import os
from datetime import datetime
import json


class Trader():
    def __init__(self, symbols, params_dict, testnet_client, data_client, bar_length, last_positions_path, symbolToUnits, initialUnit, strategy = None):
        self.symbols = symbols
        self.params_dict = params_dict
        self.testnet_client = testnet_client
        self.data_client = data_client
        self.available_intervals = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d",
                                    "1w", "1M"]
        self.bar_length = bar_length
        self.trades = 0
        self.trade_values = []
        self.price_data = None
        self.s = None
        self.last_positions = None # about positions
        self.last_positions_path = last_positions_path
        self.strategy = strategy
        self.cur_pos_path = f'./currOrders/{strategy}.csv'
        self.closed_pos_path = f'./closedOrders/{strategy}.csv'
        self.symToUnits_path = f'./symToUnits/{strategy}.csv'
        self.cur_positions = None # about orders
        self.closed_positions = None # about orders
        self.symbolToUnits = symbolToUnits
        self.initialUnit = initialUnit
        self.symToUnitsDF = None

    def get_most_recent(self, interval, days, data_client):
        now = datetime.utcnow()
        now = now.replace(minute=0, hour=0, second=0) # get data at 0, 0, 0 time only
        past = str(now - timedelta(days=days))
        price_list = []
        for symbol in self.symbols:
            data = get_historical_data(past, now, data_client, symbol, interval)
            data = data.loc["2019-01-01":]
            dataSeries = data["Open"].rename(symbol)
            price_list.append(dataSeries)
        self.price_data = pd.concat(price_list, axis=1)

    @abstractmethod
    def generate_trading_signals(self):
        while False:
            yield None


    def execute_trades(self):
        self.last_positions = pd.read_csv(self.last_positions_path)
        for symbol in self.symbols:
            # current position is long
            price = self.price_data[symbol].iloc[-1]
            if self.position_data[symbol].iloc[-1] == 1:
                # go long
                if self.last_positions[symbol].iloc[-1] == 0:
                    order = self.testnet_client.create_order(symbol=symbol, side="BUY", type="MARKET", quoteOrderQty = self.symbolToUnits[symbol])
                    self.fill_order(order)
                    self.report_trade(order, "GOING LONG", symbol)
                else:
                    print(f"{symbol}: Remain Long")
            # current position is neutral
            if self.position_data[symbol].iloc[-1] == 0:
                if self.last_positions[symbol].iloc[-1] == 1:
                    order = self.close_long_position(symbol)
                    self.report_trade(order, "GOING NEUTRAL", symbol)
                else:
                    print(f"{symbol}: Remain Neutral")
        self.last_positions = self.position_data.tail(1)
        self.last_positions.to_csv(self.last_positions_path)
        self.cur_positions.to_csv(self.cur_pos_path)
        self.closed_positions.to_csv(self.closed_pos_path)

    def start_trading(self):
        # last positions are all zero
        if not os.path.isfile(self.last_positions_path):
            last_positions = pd.DataFrame(data=0, index=[datetime.utcnow().date()], columns=self.symbols)
            last_positions.to_csv(self.last_positions_path)
            self.last_positions = last_positions
        # last position are being tracked
        else:
            self.last_positions = pd.read_csv(self.last_positions_path, index_col=[0])

        if not os.path.isfile(self.cur_pos_path):
            self.cur_positions = pd.DataFrame(columns=["symbol","time","side","entry_price","base_units","quote_units","strategy"])
        else:
            self.cur_positions = pd.read_csv(self.cur_pos_path, index_col=[0])

        if not os.path.isfile(self.closed_pos_path):
            self.closed_positions = pd.DataFrame(columns=["symbol","entryOrderId", "entryTime", "closeTime", "entryPrice",
                                                          "currentPrice", "usdtEntry","usdtExit", "usdtProfit", "closeReturn", "strategy"])
        else:
            self.closed_positions = pd.read_csv(self.closed_pos_path, index_col=[0])

        self.get_most_recent(self.bar_length, 200, self.data_client)
        self.pre_trade()
        self.generate_trading_signals()
        self.execute_trades()

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

        # if self.trades % 2 == 0:
        #     real_profit = round(np.sum(self.trade_values[-2:]), 3)
        #     self.cum_profits = round(np.sum(self.trade_values), 3)
        # else:
        #     real_profit = 0
        #     self.cum_profits = round(np.sum(self.trade_values[:-1]), 3)

        # print trade report
        print(2 * "\n" + 100 * "-")
        print("{} | {} | {}".format(time, going, symbol))
        print("{} | Base_Units = {} | Quote_Units = {} | Price = {} ".format(time, base_units, quote_units, price))
        # print("{} | Profit = {} | CumProfits = {} ".format(time, real_profit, self.cum_profits))
        print(100 * "-" + "\n")

    def fill_order(self, order):
        base_units = float(order["executedQty"])
        quote_units = float(order["cummulativeQuoteQty"])
        price = round(quote_units / base_units, 5)
        order_data = {"symbol": order['symbol'],
                      "time": pd.to_datetime(order["transactTime"], unit="ms"),
                      "side": order["side"],
                      "entry_price": price,
                      "quote_units": quote_units,
                      "base_units": base_units,
                      "strategy":self.strategy}
        self.cur_positions.loc[order["orderId"]] = order_data

    def close_long_position(self, symbol):
        orderId = self.cur_positions.index[((self.cur_positions['symbol'] == symbol) & (self.cur_positions['strategy'] ==
                                                                                     self.strategy)).argmax()]
        entryPrice = self.cur_positions.loc[orderId]['entry_price']
        usdtEntry = self.cur_positions.loc[orderId]['quote_units']
        currentPrice = float(self.testnet_client.get_symbol_ticker(symbol=symbol)["price"])
        idealusdtExit = round(usdtEntry * (currentPrice / entryPrice), 3)
        order = self.testnet_client.create_order(symbol=symbol, side="SELL", type="MARKET", quoteOrderQty=idealusdtExit)
        usdtExit = float(order["cummulativeQuoteQty"])
        usdtProfit = usdtExit - usdtEntry
        closeReturn = round(usdtProfit / usdtEntry * 100, 5)
        close_data = {"symbol": symbol,
                      "entryOrderId": orderId,
                      "entryTime": self.cur_positions.loc[orderId]["time"],
                      "closeTime": pd.to_datetime(order["transactTime"], unit="ms"),
                      "entryPrice": entryPrice,
                      "currentPrice": currentPrice,
                      "usdtEntry": usdtEntry,
                      "usdtExit": usdtExit,
                      "usdtProfit": usdtProfit,
                      "closeReturn": closeReturn,
                      "strategy": self.strategy}
        self.closed_positions.loc[order["orderId"]] = close_data
        self.cur_positions = self.cur_positions.drop(index=orderId)
        return order

    def pre_trade(self):
        now = datetime.utcnow()
        if not os.path.isfile(self.symToUnits_path):
            # trading just get started for first time
            self.symToUnitsDF = pd.DataFrame(columns=self.symbols)
            units = []
            for symbol in self.symbols:
                units.append(self.symbolToUnits[symbol])
                # self.symToUnitsDF.loc[now][symbol] = self.symbolToUnits[symbol]
            self.symToUnitsDF.loc[now] = units
            self.symToUnitsDF.to_csv(self.symToUnits_path)
        else:
            self.symToUnitsDF = pd.read_csv(self.symToUnits_path, index_col=[0])
            lastSymToUnits = self.symToUnitsDF.tail(1)
            units = []
            for symbol in self.symbols:
                # long before
                if self.last_positions[symbol].iloc[-1] == 0:
                    units.append(lastSymToUnits.tail(1)[symbol].values[0])
                else:
                    orderId = self.cur_positions.index[((self.cur_positions['symbol'] == symbol) & (self.cur_positions['strategy'] ==self.strategy)).argmax()]
                    entryPrice = self.cur_positions.loc[orderId]['entry_price']
                    usdtEntry = self.cur_positions.loc[orderId]['quote_units']
                    currentPrice = float(self.testnet_client.get_symbol_ticker(symbol=symbol)["price"])
                    idealusdtExit = round(usdtEntry * (currentPrice / entryPrice), 3)
                    units.append(round(idealusdtExit, 1))
            self.symToUnitsDF.loc[now] = units
            self.symToUnitsDF.to_csv(self.symToUnits_path)
        self.symbolToUnits = self.symToUnitsDF.tail(1).to_dict('records')[0]





