
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
class PortfolioBacktester:
    def __init__(self, positions, price_data, tc = -0.001):
        self.positions = positions
        self.price_data = price_data
        self.tc = tc
        self.return_df = None # simple return dataframe for buy and hold
        self.strategy_df = None # simple return dataframe for the strategy
        self.no_of_trades = None

    def calculate_asset_return(self):
        self.return_df = self.price_data.pct_change()
        self.return_df["portfolio_return"] = self.return_df.mean(axis = 1)# 1/n weighting
        self.return_df["cportfolio_return"] = (self.return_df["portfolio_return"]+1).cumprod()

    def calculate_strategy_return(self):
        self.no_of_trades = self.positions.diff().fillna(0).abs()
        self.strategy_df = self.price_data.pct_change() * self.positions.shift(1)
        self.strategy_df = self.strategy_df.add(self.no_of_trades * self.tc)
        self.strategy_df["portfolio_return"] = self.strategy_df.mean(axis = 1) # 1/n weighting
        self.strategy_df["cportfolio_return"] = (self.strategy_df["portfolio_return"] + 1).cumprod()
    def backtest(self):
        self.calculate_asset_return()
        self.calculate_strategy_return()

    def generate_result(self):
        self.plot_result()
        self.print_performance()

    def plot_result(self):
        title = "Backtesting result for strategy"
        plt.figure(figsize=(12, 8))
        pd.DataFrame()
        plt.title(title)
        plt.plot(self.strategy_df[["cportfolio_return"]], label = 'strategy', color = "orange")
        plt.plot(self.return_df[["cportfolio_return"]], label = 'buy and hold')
        plt.legend()
        plt.show()

    def print_performance(self):
        strategy_multiple = round(self.calculate_strategy_multiple(), 6)
        bh_multiple = round(self.calculate_return_multiple(), 6)
        outperf = round(strategy_multiple - bh_multiple, 6)
        strat_cagr = round(self.calculate_strat_cagr(), 6)
        bh_cagr = round(self.calculate_bh_cagr(), 6)
        strat_ann_std = round(self.calculate_strat_annualized_std(), 6)
        bh_ann_std = round(self.calculate_bh_annualized_std(), 6)
        strat_sharpe = round(self.calculate_strat_sharpe(), 6)
        bh_sharpe = round(self.calculate_bh_sharpe(), 6)

        print(100 * "-")
        print("PERFORMANCE MEASURES:")
        print("\n")
        print("Multiple (Strategy):         {}".format(strategy_multiple))
        print("Multiple (Buy-and-Hold):     {}".format(bh_multiple))
        print(38 * "-")
        print("Out-/Underperformance:       {}".format(outperf))
        print(100 * "-")
        print("CAGR (Strategy):                       {}".format(strat_cagr))
        print("CAGR (Buy-and-Hold):                   {}".format(bh_cagr))
        print(100 * "-")
        print("Annualized Std (Stratgy):              {}".format(strat_ann_std))
        print("Annualized Std (Buy-and-Hold):         {}".format(bh_ann_std))
        print(100 * "-")
        print("Sharpe Ratio (Strategy):               {}".format(strat_sharpe))
        print("Sharpe Ratio (Buy-and-Hold):           {}".format(bh_sharpe))

    def calculate_strategy_multiple(self):
        return np.cumprod(self.strategy_df["portfolio_return"] + 1).iloc[-1]

    def calculate_return_multiple(self):
        return np.cumprod(self.return_df["portfolio_return"] + 1).iloc[-1]

    def calculate_strat_cagr(self):
        return self.calculate_strategy_multiple() ** \
            (1 /((self.strategy_df.index[-1] - self.strategy_df.index[0]).days/365.25)) - 1
    
    def calculate_bh_cagr(self):
        return self.calculate_return_multiple() ** \
            (1 /((self.return_df.index[-1] - self.return_df.index[0]).days/365.25)) - 1

    def calculate_strat_annualized_std(self):
        return self.strategy_df["portfolio_return"].std() * np.sqrt(365.25)

    def calculate_bh_annualized_std(self):
        return self.return_df["portfolio_return"].std() * np.sqrt(365.25)

    def calculate_strat_sharpe(self):
        if self.calculate_strat_annualized_std() == 0:
            return np.nan
        else:
            return self.calculate_strat_cagr() / self.calculate_strat_annualized_std()

    def calculate_bh_sharpe(self):
        if self.calculate_bh_annualized_std() == 0:
            return np.nan
        else:
            return self.calculate_bh_cagr() / self.calculate_bh_annualized_std()

    