from abc import abstractmethod
import pandas as pd
from portfolio_backtesting import PortfolioBacktester
class Strategy:
    def __init__(self, training_period, testing_period, price_data, symbols, risk_parity_dict):
        self.symbols = symbols
        self.training_period = training_period
        self.testing_period = testing_period
        self.price_data = price_data
        self.position_data = pd.DataFrame(columns=symbols, index=price_data.index)
        self.risk_parity_dict = risk_parity_dict


    # Training = True means doing training
    # Training = False means doing testing
    # params dict # {symbol: params}
    def backtest(self, params_dict, training = True):
        for symbol, params in params_dict.items():
            self.generate_signals(symbol, params)
        if training == True:
            self.price_data = self.price_data.loc[self.training_period[0]:self.training_period[1]].copy(deep=True)
            self.position_data = self.position_data.loc[self.training_period[0]:self.training_period[1]].copy(deep=True)
        else:
            self.price_data = self.price_data.loc[self.testing_period[0]:self.testing_period[1]].copy(deep=True)
            self.position_data = self.position_data.loc[self.testing_period[0]:self.testing_period[1]].copy(deep=True)
        backtester = PortfolioBacktester(self.position_data, self.price_data, self.risk_parity_dict)
        backtester.backtest()
        backtester.generate_result()

    # pass the combinations of different parameters
    def optimise_strategy(self, symbol, combinations, training):
        price_data = self.price_data[[symbol]]
        many_results = pd.DataFrame(data=combinations)
        sharpe_results = []
        multiple_results = []
        for comb in combinations:
            self.generate_signals(symbol, comb)
            position_data = self.position_data[[symbol]]
            if training == True:
                price_data = price_data.loc[self.training_period[0]:self.training_period[1]].copy(deep=True)
                position_data = position_data.loc[self.training_period[0]:self.training_period[1]].copy(
                    deep=True)
            else:
                price_data = price_data.loc[self.testing_period[0]:self.testing_period[1]].copy(deep=True)
                position_data = position_data.loc[self.testing_period[0]:self.testing_period[1]].copy(
                    deep=True)
            backtester = PortfolioBacktester(position_data, price_data, self.risk_parity_dict)
            backtester.backtest()
            multiple_results.append(backtester.calculate_strategy_multiple())
            sharpe_results.append(backtester.calculate_strat_sharpe())
        many_results["sharpe"] = sharpe_results
        many_results["multiple"] = multiple_results
        return many_results
    @abstractmethod
    def generate_signals(self, symbol, params):
        while False:
            yield None
