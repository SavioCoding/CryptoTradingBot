import numpy as np
import matplotlib.pyplot as plt
from itertools import product
class Backtester():
    '''
    symbol = the symbol of the asset

    data = dataframe contains price data of the asset and position data of the strategy
    data should include columns 'price' and column 'position'

    tc = transaction cost of each of the trade (in percentage)
    '''
    def __init__(self, symbol, data, tc = 0):
        self.symbol = symbol
        self.data = data
        self.tc = tc
        self.tp_year = (self.data.price.count() / ((self.data.index[-1] - self.data.index[0]).days / 365.25))
        print(self.tp_year)

    def calculate_asset_log_return(self):
        self.data["returns"] = np.log(self.data["price"] / self.data["price"].shift(1))

    def calculate_strategy_log_return(self):
        self.data["strategy"] = self.data["position"].shift(1) * self.data["returns"]

    def backtest(self):
        self.calculate_asset_log_return()
        self.calculate_strategy_log_return()

        # calculate the number of trades
        self.data["trades"] = self.data.position.diff().fillna(0).abs()
        self.data.strategy = self.data.strategy.add(self.data.trades * self.tc)
        self.data["creturns"] = self.data["returns"].cumsum().apply(np.exp)
        self.data["cstrategy"] = self.data["strategy"].cumsum().apply(np.exp)

    def generate_result(self):
        self.plot_results()
        self.print_performance()
    def plot_results(self):
        title = "Backtesting result for {}".format(self.symbol)
        self.data[["creturns", "cstrategy"]].plot(title=title, figsize=(12, 8))
        plt.show()

    def print_performance(self):
        ''' Calculates and prints various Performance Metrics.
                '''

        data = self.data.copy()
        strategy_multiple = round(self.calculate_strategy_multiple(), 6)
        bh_multiple = round(self.calculate_return_multiple(), 6)
        outperf = round(strategy_multiple - bh_multiple, 6)
        cagr = round(self.calculate_cagr(), 6)
        ann_mean = round(self.calculate_annualized_mean(), 6)
        ann_std = round(self.calculate_annualized_std(), 6)
        sharpe = round(self.calculate_sharpe(), 6)

        print(100 * "-")
        print("PERFORMANCE MEASURES:")
        print("\n")
        print("Multiple (Strategy):         {}".format(strategy_multiple))
        print("Multiple (Buy-and-Hold):     {}".format(bh_multiple))
        print(38 * "-")
        print("Out-/Underperformance:       {}".format(outperf))
        print("\n")
        print("CAGR:                        {}".format(cagr))
        print("Annualized Mean:             {}".format(ann_mean))
        print("Annualized Std:              {}".format(ann_std))
        print("Sharpe Ratio:                {}".format(sharpe))

        print(100 * "=")

    def calculate_strategy_multiple(self):
        series = self.data["strategy"]
        return np.exp(series.sum())

    def calculate_return_multiple(self):
        series = self.data["returns"]
        return np.exp(series.sum())
    def calculate_cagr(self):
        series = self.data["strategy"]
        return np.exp(series.sum()) ** (1 / ((series.index[-1] - series.index[0]).days / 365.25)) - 1

    def calculate_annualized_mean(self):
        series = self.data["strategy"]
        return series.mean() * self.tp_year

    def calculate_annualized_std(self):
        series = self.data["strategy"]
        return series.std() * np.sqrt(self.tp_year)

    def calculate_sharpe(self):
        series = self.data["strategy"]
        if series.std() == 0:
            return np.nan
        else:
            return self.calculate_cagr() / self.calculate_annualized_std()





