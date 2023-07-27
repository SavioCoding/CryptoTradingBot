from Traders import Trader
from dataapi import api_key as data_api, secret_key as data_secret
from testapi import api_key as testnet_api, secret_key as testnet_secret
from binance.client import Client
from strategies.BreakoutStrategy import Breakout
import json

class BreakoutTrader(Trader.Trader):
    def __init__(self, symbols, params_dict, usdtunits, testnet_client, data_client, bar_length, last_positions_path):
        super().__init__(symbols, params_dict, usdtunits, testnet_client, data_client, bar_length, last_positions_path)

    def generate_trading_signals(self):
        breakoutStrat = Breakout(None, None, self.price_data.copy(), self.symbols)
        for symbol, params in self.params_dict.items():
            breakoutStrat.generate_signals(symbol, params)
        self.position_data = breakoutStrat.position_data


if __name__ == "__main__":  # only if we run MACtrader.py as a script, please do the following:
    testnet_client = Client(api_key=testnet_api, api_secret=testnet_secret, tld="com", testnet=True)
    data_client = Client(api_key=data_api, api_secret=data_secret, tld="com")
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "LTCUSDT", "TRXUSDT", "XRPUSDT"]
    params_dict = json.load(open("./params/Breakout.txt"))
    bar_length = "1d"
    units = 50 # e.g each trade use 50 usdt
    last_positions_path = "./positions/Breakout.csv"
    trader = BreakoutTrader(symbols=symbols, params_dict = params_dict, usdtunits=units, testnet_client=testnet_client,
                            data_client = data_client, bar_length = "1d", last_positions_path = last_positions_path)
    trader.start_trading()
