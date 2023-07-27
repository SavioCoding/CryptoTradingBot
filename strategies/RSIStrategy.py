from strategies.Strategy import Strategy
import pandas as pd
import numpy as np

class RSI(Strategy):
    def __init__(self, training_period, testing_period, price_data, symbols):
        super().__init__(training_period, testing_period, price_data, symbols)

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
    # window (int) and long window (int) to generate signals
    def generate_signals(self, symbol, params):
        days = int(params[0])
        RSI = self.get_rsi(symbol, days)
        RSI[RSI <= 30] = 1
        RSI[RSI >= 70] = -1
        RSI[(RSI > 30) & (RSI < 70)] = 0
        self.position_data[symbol] = RSI


    def backtest(self, params_dict, training):
        super().backtest(params_dict, training)

    def optimise_strategy(self, windows, training):
        combinations = [(period, None) for period in windows]
        # pass the combinations of parameters to the parent class
        params_dict = {}
        for i in range(len(symbols)):
            combine_results = super().optimise_strategy(self.symbols[i], combinations, training)
            print(f"Performance of {self.symbols[i]}:")
            print("Top 5 Sharpe Ratio: \n")
            print(combine_results.nlargest(5, "sharpe"))
            print("\n")
            params_dict[self.symbols[i]] = (combine_results.nlargest(1, "sharpe").iloc[0, :][0], combine_results.nlargest(1, "sharpe").iloc[0, :][1])
        return params_dict
            # print("Top 5 cumulative return: \n")
            # print(combine_results.nlargest(5, "multiple"))


if __name__ == "__main__":

    # read the data
    symbols = ["BTCUSDT", "ETHUSDT","BNBUSDT","LTCUSDT","TRXUSDT","XRPUSDT"]
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
    RSIStrat = RSI(training_period, testing_period, price_data, symbols)
    # # True means training, False means testing
    windows = [5, 7, 9, 11, 13, 15]
    params_dict = RSIStrat.optimise_strategy(windows, True)
    print(params_dict)
    # params_dict = {'BTCUSDT': (5.0, 100.0), 'ETHUSDT': (15.0, 50.0), 'BNBUSDT': (5.0, 50.0), 'LTCUSDT': (15.0, 50.0), 'TRXUSDT': (5.0, 50.0), 'XRPUSDT': (10.0, 25.0)}
    # found (5, 100) is the best combination for BTCUSDT
    # found (15, 50) is the best combination for ETHUSDT
    # found (5, 50) is the best combination for BNBUSDT
    # found (15 ,50) is the best combination for LTCUSDT
    # found (5, 50) is the best combination for TRXUSDT
    # found (10, 25) is the best combination for XRPUSDT

    RSIStrat.backtest(params_dict, False)
