from strategies.Strategy import Strategy
import pandas as pd
import json
import numpy as np
class Breakout(Strategy):
    def __init__(self, training_period, testing_period, price_data, symbols, risk_parity_dict):
        super().__init__(training_period, testing_period, price_data, symbols, risk_parity_dict)

    def backtest(self, params, training):
        super().backtest(params, training)

    # high and low days to generate signals
    def generate_signals(self,symbol, params):
        # if high than 20 days high buy, lower than 10 days low sell
        high = int(params[0]) # 20
        low = int(params[1]) # 10
        self.price_data['Buy'] = self.price_data[symbol].rolling(window=high, min_periods=1).max()
        self.price_data['Sell'] = self.price_data[symbol].rolling(window=low, min_periods=1).min()
        positions = []
        i = 0
        for idx, row in self.price_data.iterrows():
            if i == 0:
                positions.append(0) # initial position must be 0
                i = 1
            elif row[symbol] == row['Buy']:
                positions.append(1)
            elif row[symbol] == row["Sell"]:
                positions.append(0)
            else:
                positions.append(positions[-1])
        self.position_data[symbol] = positions
        self.price_data = self.price_data.drop(columns=["Buy", "Sell"])

    def optimise_strategy(self, high_days, low_days, training):
        params_dict = {}
        for i in range(len(self.symbols)):
            combinations = []
            for high in high_days:
                for low in low_days:
                    if low < high:
                        combinations.append((high, low))
                    else:
                        continue
            # pass the combinations of parameters to the parent class
            combine_results = super().optimise_strategy(self.symbols[i], combinations, training)
            print(f"Performance of {self.symbols[i]}:")
            print("Top 5 Sharpe Ratio: \n")
            print(combine_results.nlargest(5, "sharpe"))
            print("\n")
            params_dict[self.symbols[i]] = (combine_results.nlargest(1, "sharpe").iloc[0, :][0], combine_results.nlargest(1, "sharpe").iloc[0, :][1])
        return params_dict

if __name__ == "__main__":
    # read the data
    symbols = ["BTCUSDT", "ETHUSDT", "LTCUSDT", "TRXUSDT", "XRPUSDT"]
    price_list = []
    for symbol in symbols:
        data = pd.read_csv(f"../data/{symbol}-1d.csv", parse_dates=["Date"], index_col="Date")
        data = data.loc["2019-01-01":]
        dataSeries = data["Close"].rename(symbol)
        price_list.append(dataSeries)
    # filter the data needed
    with open('../risk_parity.json', 'r') as fp:
        risk_parity_dict = json.load(fp)
    price_data = pd.concat(price_list, axis=1)
    training_period = ("2020-01-01", "2020-12-31")
    testing_period = ("2021-01-01", "2023-05-31")


    breakoutStrat = Breakout(training_period, testing_period, price_data, symbols, risk_parity_dict)
    # True means training, False means testing

    low_days = [5, 10, 15, 20, 25, 30, 40, 50]
    high_days = [10, 25, 50, 75, 100, 150]
    params_dict = breakoutStrat.optimise_strategy(high_days, low_days, True)
    print("Best parameters combinations for training : ")
    print(params_dict)
    json.dump(params_dict, open("../params/Breakout.txt", 'w'))
    breakoutStrat.backtest(params_dict, False)
    # found (5, 100) is the best combination
    #
    #
