from strategies.Strategy import Strategy
import pandas as pd
import numpy as np
import json

class Momentum(Strategy):
    def __init__(self, training_period, testing_period, price_data, symbols, risk_parity_dict):
        super().__init__(training_period, testing_period, price_data, symbols, risk_parity_dict)
        self.returns = self.price_data.pct_change()
        self.rolling_return = None

    # window (int) and long window (int) to generate signals
    def generate_signals(self, symbol, params):
        # Calculate returns first
        period = params[0]
        self.rolling_return = (self.returns + 1).rolling(period).apply(np.prod) - 1
        self.position_data[symbol] = np.where(self.rolling_return[symbol] > 0, 1, 0)
    def backtest(self, params_dict, training):
        super().backtest(params_dict, training)

    def optimise_strategy(self, periods, training):
        combinations = [(period,None) for period in periods]
        # pass the combinations of parameters to the parent class
        params_dict = {}
        for i in range(len(symbols)):
            combine_results = super().optimise_strategy(self.symbols[i], combinations, training)
            print(f"Performance of {self.symbols[i]}:")
            print("Top 5 Sharpe Ratio: \n")
            print(combine_results.nlargest(5, "sharpe"))
            print("\n")
            params_dict[self.symbols[i]] = (int(combine_results.nlargest(1, "sharpe").iloc[0,:][0]),None)
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
    training_period = ("2020-01-01", "2020-12-31")
    testing_period = ("2021-01-01", "2023-05-31")
    with open('../risk_parity.json', 'r') as fp:
        risk_parity_dict = json.load(fp)
    momentumStrat = Momentum(training_period, testing_period, price_data, symbols, risk_parity_dict)
    # # True means training, False means testing
    periods = (10, 20, 30, 90, 180)
    params_dict = momentumStrat.optimise_strategy(periods, True)
    print("Best parameters combinations for training : ")
    print(params_dict)
    json.dump(params_dict, open("../params/Momentum.txt", 'w'))
    # params_dict = {'BTCUSDT': (5.0, 100.0), 'ETHUSDT': (15.0, 50.0), 'BNBUSDT': (5.0, 50.0), 'LTCUSDT': (15.0, 50.0), 'TRXUSDT': (5.0, 50.0), 'XRPUSDT': (10.0, 25.0)}
    # found (5, 100) is the best combination for BTCUSDT
    # found (15, 50) is the best combination for ETHUSDT
    # found (5, 50) is the best combination for BNBUSDT
    # found (15 ,50) is the best combination for LTCUSDT
    # found (5, 50) is the best combination for TRXUSDT
    # found (10, 25) is the best combination for XRPUSDT

    momentumStrat.backtest(params_dict, False)
