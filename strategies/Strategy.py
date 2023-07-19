from abc import abstractmethod
import pandas as pd
from portfolio_backtesting import PortfolioBacktester
class Strategy:
    def __init__(self, training_period, testing_period, price_data):
        self.training_period = training_period
        self.testing_period = testing_period
        self.price_data = price_data

    # Training = True means doing training
    # Training = False means doing testing
    def backtest(self, params, training = True):
        self.generate_signals(params)
        if training == True:
            self.price_data = self.price_data.loc[self.training_period[0]:self.training_period[1]].copy(deep=True)
        else:
            self.price_data = self.price_data.loc[self.testing_period[0]:self.testing_period[1]].copy(deep=True)
        backtester = PortfolioBacktester(self.price_data[["position"]], self.price_data[["price"]])
        backtester.backtest()
        backtester.generate_result()

    # pass the combinations of different parameters
    def optimise_strategy(self, combinations):
        many_results = pd.DataFrame(data=combinations)
        sharpe_results = []
        multiple_results = []
        for comb in combinations:
            self.generate_signals(comb)
            backtester = PortfolioBacktester(self.price_data[["position"]], self.price_data[["price"]])
            backtester.backtest()
            multiple_results.append(backtester.calculate_strategy_multiple())
            sharpe_results.append(backtester.calculate_strategy_multiple())
        many_results["sharpe"] = sharpe_results
        many_results["multiple"] = multiple_results
        return many_results
    @abstractmethod
    def generate_signals(self, params):
        while False:
            yield None
