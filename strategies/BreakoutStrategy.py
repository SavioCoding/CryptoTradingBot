from Strategy import Strategy
import pandas as pd

class Breakout(Strategy):
    def __init__(self, training_period, testing_period, price_data):
        super().__init__(training_period, testing_period, price_data)

    def backtest(self, params, training):
        super().backtest(params, training)

    def generate_signals(self, params):
        # if high than 20 days high buy, lower than 10 days low sell
        high = params[0] # 20
        low = params[1] # 10
        self.price_data['Buy'] = self.price_data['price'].rolling(window=high, min_periods=1).max()
        self.price_data['Sell'] = self.price_data['price'].rolling(window=low, min_periods=1).min()
        positions = []
        i = 0
        for idx, row in self.price_data.iterrows():
            if i == 0:
                positions.append(0) # initial position must be 0
                i = 1
            elif row["price"] == row['Buy']:
                positions.append(1)
            elif row["price"] == row["Sell"]:
                positions.append(0)
            else:
                positions.append(positions[-1])
        self.price_data['position'] = positions

    def optimise_strategy(self, high_days, low_days):
        combinations = []
        for high in high_days:
            for low in low_days:
                if low < high:
                    combinations.append((high, low))
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


    breakout = Breakout(training_period, testing_period, price_data)
    params = (25, 20)

    # True means training, False means testing
    breakout.backtest(params, True)
    low_days = [5, 10, 15, 20, 25, 30, 40, 50]
    high_days = [10, 25, 50, 75, 100, 150, 200]
    breakout.optimise_strategy(high_days, low_days)
    # found (5, 100) is the best combination
    #
    #
