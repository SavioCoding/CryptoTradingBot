import numpy as np
from pylab import plt
import math
import pandas as pd
from scipy.optimize import minimize

BTCUSDT = pd.read_csv("./data/BTCUSDT-1d.csv", parse_dates=["Date"], index_col="Date")
ETHUSDT = pd.read_csv("./data/ETHUSDT-1d.csv", parse_dates=["Date"], index_col="Date")
LTCUSDT = pd.read_csv("./data/LTCUSDT-1d.csv", parse_dates=["Date"], index_col="Date")
TRXUSDT = pd.read_csv("./data/TRXUSDT-1d.csv", parse_dates=["Date"], index_col="Date")
XRPUSDT = pd.read_csv("./data/XRPUSDT-1d.csv", parse_dates=["Date"], index_col="Date")

Date = "2019-01-01"
prices = pd.DataFrame(columns=["BTCUSDT","ETHUSDT","LTCUSDT","TRXUSDT","XRPUSDT"])
# pd.DataFrame([BNBUSDT["Close"].loc["2019-01-01":], BTCUSDT["Close"].loc["2019-01-01":],
#               ETHUSDT["Close"].loc["2019-01-01":], LTCUSDT["Close"].loc["2019-01-01":],
#               TRXUSDT["Close"].loc["2019-01-01":], XRPUSDT["Close"].loc["2019-01-01":]],
#              columns=["BNBUSDT","BTCUSDT","ETHUSDT","LTCUSDT","TRXUSDT","XRPUSDT"])
# prices["BNBUSDT"] = BNBUSDT["Close"].loc["2019-01-01":]
prices["BTCUSDT"] = BTCUSDT["Close"].loc["2019-01-01":]
prices["ETHUSDT"] = ETHUSDT["Close"].loc["2019-01-01":]
prices["LTCUSDT"] = LTCUSDT["Close"].loc["2019-01-01":]
prices["TRXUSDT"] = TRXUSDT["Close"].loc["2019-01-01":]
prices["XRPUSDT"] = XRPUSDT["Close"].loc["2019-01-01":]

rets = prices.pct_change()
noa = len(prices.columns)
phi = np.array(noa * [1 / noa])
def portfolio_return(weights, rets):
    return np.dot(weights.T, rets.mean()) * 252

def portfolio_variance(weights, rets):
    return np.dot(weights.T, np.dot(rets.cov(), weights)) * 252

def portfolio_volatility(weights, rets):
    return math.sqrt(portfolio_variance(weights, rets))

def rel_risk_contributions(weights, rets = rets):
    vol = portfolio_volatility(weights, rets)
    cov = rets.cov()
    mvols = np.dot(cov, weights) / vol
    rc = mvols * weights
    rrc = rc / rc.sum()
    return rrc

def mse_risk_contributions(weights, target, rets=rets):
    rc = rel_risk_contributions(weights, rets)
    mse = ((rc - target) ** 2).mean()
    return mse * 100

bnds = noa * [(0, 1),]
cons = {'type': 'eq', 'fun': lambda weights: weights.sum() - 1}
target = noa * [1 / noa,]
opt = minimize(lambda w: mse_risk_contributions(w, target=target),
               phi, bounds=bnds, constraints=cons)
phi_ = opt['x']
plt.pie(phi_, labels=prices.columns, autopct='%1.1f%%')
plt.title('Optimal Portfolio Weights')
print(phi_)