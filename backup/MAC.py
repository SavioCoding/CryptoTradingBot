import pandas as pd
import numpy as np
from backup.backtesting import Backtester
from portfolio_backtesting import PortfolioBacktester


#
def optimise_strategy(price_data, training_period, short_windows, long_windows):
    combinations = []
    for short in short_windows:
        for long in long_windows:
            if short < long:
                combinations.append((short, long))
            else:
                continue

    many_results = pd.DataFrame(data = combinations, columns = ["short_window", "long_window"])
    sharpe_results = []
    multiple_results = []
    for comb in combinations:
        data_cp = price_data.copy()
        data_cp = generate_signals(data_cp, training_period, comb[0], comb[1])
        data_cp = data_cp[["Close", "position"]]
        data_cp = data_cp.rename(columns={"Close": "price"})
        backtester = Backtester("BTCUSDT", data_cp, 0)
        backtester.backtest()
        multiple_results.append(backtester.calculate_strategy_multiple())
        sharpe_results.append(backtester.calculate_sharpe())
    many_results["sharpe"] = sharpe_results
    many_results["multiple"] = multiple_results
    return many_results
def generate_signals(price_data, training_period, short_window, long_window):
    price_data['ShortSMA'] = price_data['Close'].rolling(window=short_window, min_periods=1).mean()
    price_data['LongSMA'] = price_data['Close'].rolling(window=long_window, min_periods=1).mean()
    price_data = price_data.loc[training_period[0]:training_period[1]].copy(deep=True)
    price_data['position'] = np.where(price_data['ShortSMA'] > price_data['LongSMA'], 1, 0)
    return price_data

if __name__ == "__main__":
    data = pd.read_csv("../data/BTCUSDT-1d.csv", parse_dates=["Date"], index_col="Date")

    training_period = ("2020-01-01", "2022-12-31")  # three years of backtesting
    testing_period = ("2023-01-01", "2023-05-31")

    short_windows = [5, 10, 15, 20, 25, 30, 40, 50]
    long_windows = [25, 50, 75, 100, 150, 200]

    # combine_results = optimise_strategy(data, training_period, short_windows, long_windows)

    # print(combine_results.nlargest(5, 'sharpe'))
    # we observe that short_window 5 and long_window 100 gives the best sharpe

    df = generate_signals(data, training_period, 5, 100)

    df = df[["Close", "position"]]
    df = df.rename(columns={"Close": "price"})

    # backtester = Backtester("BTCUSDT", df)
    # backtester.backtest()
    # backtester.generate_result()

    PortfolioBacktester = PortfolioBacktester(df[["position"]], df[["price"]])
    PortfolioBacktester.backtest()
    PortfolioBacktester.generate_result()

