from Strategy import Strategy
import pandas as pd
import numpy as np

class MAC(Strategy):
    def __init__(self, training_period, testing_period, price_data):
        super().__init__(training_period, testing_period, price_data)

    # pass short window (int) and long window (int) to generate signals
    def generate_signals(self, params):
        short_window = params[0]
        long_window = params[1]
        self.price_data['ShortSMA'] = self.price_data['price'].rolling(window=short_window, min_periods=1).mean()
        self.price_data['LongSMA'] = self.price_data['price'].rolling(window=long_window, min_periods=1).mean()
        self.price_data['position'] = np.where(self.price_data['ShortSMA'] > self.price_data['LongSMA'], 1, 0)

    def backtest(self, params, training):
        super().backtest(params, training)

    def optimise_strategy(self, short_windows, long_windows):
        combinations = []
        for short in short_windows:
            for long in long_windows:
                if short < long:
                    combinations.append((short, long))
                else:
                    continue
        # pass the combinations of parameters to the parent class
        combine_results = super().optimise_strategy(combinations)
        print("Top 5 Sharpe Ratio: \n")
        print(combine_results.nlargest(5, "sharpe"))
        print("Top 5 cumulative result: \n")
        print(combine_results.nlargest(5, "multiple"))


if __name__ == "__main__":

    # read the data
    symbol = "BTCUSDT"
    data = pd.read_csv("../data/BTCUSDT-1d.csv", parse_dates=["Date"], index_col="Date")

    # filter the data needed
    price_data = data[["Close"]].rename(columns={"Close": "price"})
    training_period = ("2020-01-01", "2022-12-31")
    testing_period = ("2023-01-01", "2023-05-31")


    macStrat = MAC(training_period, testing_period, price_data)
    params = (5, 100)

    # True means training, False means testing
    macStrat.backtest(params, True)
    # short_windows = [5, 10, 15, 20, 25, 30, 40, 50]
    # long_windows = [25, 50, 75, 100, 150, 200]
    # macStrat.optimise_strategy(short_windows, long_windows)
    # found (5, 100) is the best combination
    #
