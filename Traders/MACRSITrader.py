from Traders import Trader
from dataapi import api_key as data_api, secret_key as data_secret
from testapi import api_key as testnet_api, secret_key as testnet_secret
from binance.client import Client
from strategies.MACRSIStrategy import MACRSI
import json

class MACRSITrader(Trader.Trader):
    def __init__(self, symbols, params_dict, testnet_client, data_client, bar_length, last_positions_path,
                 symbolToUnits, initialUnit, strategy):
        super().__init__(symbols, params_dict, testnet_client, data_client, bar_length, last_positions_path,
                         symbolToUnits, initialUnit, strategy)

    def generate_trading_signals(self):
        macRSIStrat = MACRSI(None, None, self.price_data.copy(), self.symbols, None)
        for symbol, params in self.params_dict.items():
            macRSIStrat.generate_signals(symbol, params)
        self.position_data = macRSIStrat.position_data
        print(self.position_data.tail(30))


if __name__ == "__main__":  # only if we run MACtrader.py as a script, please do the following:
    testnet_client = Client(api_key=testnet_api, api_secret=testnet_secret, tld="com", testnet=True)
    strategy = "MACRSI"
    data_client = Client(api_key=data_api, api_secret=data_secret, tld="com")
    symbols = ["BTCUSDT", "ETHUSDT", "LTCUSDT", "TRXUSDT", "XRPUSDT"]
    params_dict = json.load(open("./params/MACRSI.txt"))
    bar_length = "1d"
    initial_units = 500
    with open('./risk_parity.json', 'r') as fp:
        risk_parity_dict = json.load(fp)
    symbolToUnits = {}
    for key, value in risk_parity_dict.items():
        symbolToUnits[key] = round(initial_units * value, 1)
    last_positions_path = "./positions/MACRSI.csv"
    trader = MACRSITrader(symbols=symbols, params_dict = params_dict, testnet_client=testnet_client,
                        data_client = data_client, bar_length = "1d", last_positions_path = last_positions_path,
                        symbolToUnits=symbolToUnits, initialUnit = initial_units, strategy = strategy)
    trader.start_trading()
