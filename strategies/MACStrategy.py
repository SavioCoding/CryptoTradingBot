from strategies.Strategy import Strategy
import pandas as pd
import numpy as np
import json

class MAC(Strategy):
    def __init__(self, training_period, testing_period, price_data, symbols, risk_parity_dict):
        super().__init__(training_period, testing_period, price_data, symbols, risk_parity_dict)

    # window (int) and long window (int) to generate signals
    def generate_signals(self, symbol, params):
        short_window = int(params[0])
        long_window = int(params[1])
        shortSMA = self.price_data[symbol].rolling(window=short_window, min_periods=1).mean()
        longSMA = self.price_data[symbol].rolling(window=long_window, min_periods=1).mean()
        self.position_data[symbol] = np.where(shortSMA > longSMA, 1, 0)
    def backtest(self, params_dict, training):
        super().backtest(params_dict, training)

    def optimise_strategy(self, short_windows, long_windows, training):
        params_dict = {}
        for i in range(len(self.symbols)):
            combinations = []
            for short in short_windows:
                for long in long_windows:
                    if short < long:
                        combinations.append((short, long))
                    else:
                        continue
            # pass the combinations of parameters to the parent class
            combine_results = super().optimise_strategy(self.symbols[i], combinations, training)
            print(f"Performance of {self.symbols[i]}:")
            print("Top 5 Sharpe Ratio: \n")
            print(combine_results.nlargest(5, "sharpe"))
            print("\n")
            params_dict[self.symbols[i]] = (combine_results.nlargest(1, "sharpe").iloc[0,:][0], combine_results.nlargest(1, "sharpe").iloc[0,:][1])
        return params_dict
            # print("Top 5 cumulative return: \n")
            # print(combine_results.nlargest(5, "multiple"))


if __name__ == "__main__":

    # read the data
    symbols = ["BTCUSDT", "ETHUSDT","LTCUSDT","TRXUSDT","XRPUSDT"]
    price_list = []
    for symbol in symbols:
        data = pd.read_csv(f"../data/{symbol}-1d.csv", parse_dates=["Date"], index_col="Date")
        data = data.loc["2019-01-01":]
        dataSeries = data["Close"].rename(symbol)
        price_list.append(dataSeries)
    # filter the data needed
    price_data = pd.concat(price_list, axis = 1)
    training_period = ("2020-01-01", "2021-12-31")
    testing_period = ("2022-01-01", "2023-05-31")
    with open('../risk_parity.json', 'r') as fp:
        risk_parity_dict = json.load(fp)
    macStrat = MAC(training_period, testing_period, price_data, symbols, risk_parity_dict)
    # # True means training, False means testing
    short_windows = [5, 10, 15, 20, 25, 30, 40, 50]
    long_windows = [25, 50, 75, 100, 150]
    params_dict = macStrat.optimise_strategy(short_windows, long_windows, True)
    print(params_dict)
    json.dump(params_dict, open("../params/MAC.txt", 'w'))

    # params_dict = {'BTCUSDT': (5.0, 100.0), 'ETHUSDT': (15.0, 50.0), 'BNBUSDT': (5.0, 50.0), 'LTCUSDT': (15.0, 50.0), 'TRXUSDT': (5.0, 50.0), 'XRPUSDT': (10.0, 25.0)}
    # found (5, 100) is the best combination for BTCUSDT
    # found (15, 50) is the best combination for ETHUSDT
    # found (5, 50) is the best combination for BNBUSDT
    # found (15 ,50) is the best combination for LTCUSDT
    # found (5, 50) is the best combination for TRXUSDT
    # found (10, 25) is the best combination for XRPUSDT
    macStrat.backtest(params_dict, False)
