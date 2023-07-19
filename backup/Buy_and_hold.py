import pandas as pd
from backup.backtesting import Backtester

if __name__ == '__main__':
    data = pd.read_csv("../data/BTCUSDT-1d.csv", parse_dates = ["Date"], index_col ="Date")

    training_period = ("2019-06-01", "2022-05-31") # three years of backtesting
    testing_period = ("2022-06-01", "2023-05-31")

    data["position"] = 1

    data = data.loc[training_period[0]:training_period[1]]

    data = data[["Close","position"]]
    data.rename(columns={"Close":"price"})

    backtester = Backtester("BTCUSDT", data, 0)
    backtester.backtest()



