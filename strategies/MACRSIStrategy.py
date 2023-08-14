from strategies.Strategy import Strategy
import pandas as pd
import numpy as np
import json

class MACRSI(Strategy):
    def __init__(self, training_period, testing_period, price_data, symbols, risk_parity_dict):
        super().__init__(training_period, testing_period, price_data, symbols, risk_parity_dict)

    def get_rsi(self, symbol, days):
        delta = self.price_data[symbol].diff(1)
        positive = delta.copy()
        negative = delta.copy()
        positive[positive < 0] = 0
        negative[negative > 0] = 0
        average_gain = positive.rolling(window=days).mean()
        average_loss = abs(negative.rolling(window=days).mean())
        relative_strength = average_gain / average_loss
        RSI = 100 - (100 / (1 + relative_strength))
        return RSI

    def set_condition(self, shortSMA, longSMA, RSI):
        if shortSMA > longSMA and RSI < 70:
            return 1
        else:
            return 0

    # window (int) and long window (int) to generate signals
    def generate_signals(self, symbol, params):
        short_window = int(params[0])
        long_window = int(params[1])
        periods = int(params[2])
        shortSMA = self.price_data[symbol].rolling(window=short_window, min_periods=1).mean()
        longSMA = self.price_data[symbol].rolling(window=long_window, min_periods=1).mean()
        RSI = self.get_rsi(symbol, periods)
        df = pd.concat([shortSMA, longSMA, RSI], axis=1)
        df.columns.values[0] = 'shortSMA'
        df.columns.values[1] = 'longSMA'
        df.columns.values[2] = 'RSI'
        self.position_data[symbol] = df.apply(lambda x: self.set_condition(x.shortSMA, x.longSMA, x.RSI), axis = 1)


    def backtest(self, params_dict, training):
        super().backtest(params_dict, training)

    def optimise_strategy(self, short_windows, long_windows, periods, training):
        params_dict = {}
        for i in range(len(self.symbols)):
            combinations = []
            for short in short_windows:
                for long in long_windows:
                    for period in periods:
                        if short < long:
                            combinations.append((short, long, period))
                        else:
                            continue
            # pass the combinations of parameters to the parent class
            combine_results = super().optimise_strategy(self.symbols[i], combinations, training)
            print(f"Performance of {self.symbols[i]}:")
            print("Top 5 Sharpe Ratio: \n")
            print(combine_results.nlargest(5, "sharpe"))
            print("\n")
            params_dict[self.symbols[i]] = (combine_results.nlargest(1, "sharpe").iloc[0,:][0], combine_results.nlargest(1, "sharpe").iloc[0,:][1], combine_results.nlargest(1, "sharpe").iloc[0,:][2])
        return params_dict
            # print("Top 5 cumulative return: \n")
            # print(combine_results.nlargest(5, "multiple"))


if __name__ == "__main__":

    # read the data
    symbols = ["BTCUSDT", "ETHUSDT","LTCUSDT","TRXUSDT","XRPUSDT"]
    price_list = []
    with open('../risk_parity.json', 'r') as fp:
        risk_parity_dict = json.load(fp)
    for symbol in symbols:
        data = pd.read_csv(f"../data/{symbol}-1d.csv", parse_dates=["Date"], index_col="Date")
        data = data.loc["2019-01-01":]
        dataSeries = data["Close"].rename(symbol)
        price_list.append(dataSeries)
    # filter the data needed
    price_data = pd.concat(price_list, axis = 1)
    training_period = ("2020-01-01", "2020-12-31")
    testing_period = ("2021-01-01", "2023-05-31")
    macrsiStrat = MACRSI(training_period, testing_period, price_data, symbols, risk_parity_dict)
    # # True means training, False means testing
    short_windows = [5, 10, 15, 20, 25, 30, 40, 50]
    long_windows = [25, 50, 75, 100, 150]
    periods = [5, 7, 9, 11, 13, 15]
    params_dict = macrsiStrat.optimise_strategy(short_windows, long_windows, periods, True)
    print("Best parameters combinations for training : ")
    print(params_dict)
    json.dump(params_dict, open("../params/MACRSI.txt", 'w'))
    # params_dict = {'BTCUSDT': (5.0, 100.0), 'ETHUSDT': (15.0, 50.0), 'BNBUSDT': (5.0, 50.0), 'LTCUSDT': (15.0, 50.0), 'TRXUSDT': (5.0, 50.0), 'XRPUSDT': (10.0, 25.0)}
    # found (5, 100) is the best combination for BTCUSDT
    # found (15, 50) is the best combination for ETHUSDT
    # found (5, 50) is the best combination for BNBUSDT
    # found (15 ,50) is the best combination for LTCUSDT
    # found (5, 50) is the best combination for TRXUSDT
    # found (10, 25) is the best combination for XRPUSDT

    macrsiStrat.backtest(params_dict, False)