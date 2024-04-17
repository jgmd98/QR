import numpy as np
from yahooquery import Ticker
import pandas as pd
from pandas.tseries.offsets import BDay

class equitiesAnalytics:
    def __init__(self, tickerList):
        self.tickers = tickerList
        self.data = Ticker(tickerList, asynchronous=True)

    def getHistStockPrices(self, tickerList = [], period = "1y", interval = "1d", start = "", end = ""):
        # goal: get historical stock prices for a ticker list, period, and interval
        if tickerList == []:
            tickerList = self.tickers
        if start != "" and end != "":
            histStockPrices = self.data.history(start = start, end = end, interval=interval).reset_index()
        else:
            histStockPrices = self.data.history(period=period, interval=interval).reset_index()
        histStockPrices = histStockPrices[histStockPrices["symbol"].isin(tickerList)]
        return histStockPrices
    
    def getCumulativeReturn(self, tickerList = [], period = "1y", interval = "1d", start = "", end = ""):
        # goal: get cumulative return time series
        cumReturn = self.getHistStockPrices(tickerList, period, interval, start, end)
        if "adjclose" in cumReturn.columns:
            cumReturn["Return"] = cumReturn.groupby(["symbol"])["adjclose"].pct_change().fillna(0)
        else:
            cumReturn["Return"] = cumReturn.groupby(["symbol"])["close"].pct_change().fillna(0)
        cumReturn["Cumulative Return"] = 1 + cumReturn["Return"]
        cumReturn["Cumulative Return"] = 100 * cumReturn.groupby(["symbol"])["Cumulative Return"].cumprod()
        return cumReturn
    
    def getSummRetMetrics(self, tickerList = [], period = "1y", interval = "1d", start = "", end = ""):
        # goal: Get summary return metrics
        returns = self.getCumulativeReturn(tickerList, period, interval, start, end)
        scalingFactor = {"1m":252*8*60, "2m":252*8*30, "5m":252*8*12, "15m":252*8*4, "30m":252*8*2, "60m":252*8, "90m":252*8*(2/3), 
                         "1h":252*8, "1d":252, "5d":252/5, "1wk":252/5, "1mo":252/21, "3mo":252/63}[interval]
        # annualized and cumulative returns over the period
        summRetMetrics = (returns.groupby("symbol")["Return"].mean()*scalingFactor*100).to_frame("Annualized Return")
        summRetMetrics["Annualized Volatility"] = (returns.groupby("symbol")["Return"].std()*np.sqrt(scalingFactor)*100).to_frame("Annualized Volatility")
        summRetMetrics["Annualized Sharpe"] = summRetMetrics["Annualized Return"] / summRetMetrics["Annualized Volatility"]
        summRetMetrics["Cumulative Return"] = -100 + returns.groupby("symbol").last()["Cumulative Return"]
        # trailing returns from end date
        summRetMetrics["1m Return"] = -100 + self.getCumulativeReturn(tickerList, "1m", "1d", start=(pd.to_datetime(end) - BDay(21)).strftime("%Y-%m-%d"), end=end).groupby("symbol").last()["Cumulative Return"]
        summRetMetrics["3m Return"] = -100 + self.getCumulativeReturn(tickerList, "3m", "1d", start=(pd.to_datetime(end) - BDay(63)).strftime("%Y-%m-%d"), end=end).groupby("symbol").last()["Cumulative Return"]
        summRetMetrics["1y Return"] = -100 + self.getCumulativeReturn(tickerList, "1y", "1d", start="", end=end).groupby("symbol").last()["Cumulative Return"]
        summRetMetrics["2y Return"] = -100 + self.getCumulativeReturn(tickerList, "2y", "1d", start="", end=end).groupby("symbol").last()["Cumulative Return"]
        summRetMetrics["3y Return"] = -100 + self.getCumulativeReturn(tickerList, "3y", "1d", start="", end=end).groupby("symbol").last()["Cumulative Return"]
        return round(summRetMetrics, 2)
    
    def getFundamentals(self, tickerList = [], method = "all", argFreq = "a", argTrailing = True, metrics = ["TotalDebt", "TotalAssets", 
                                                                                                            "EBIT", "EBITDA", "PeRatio"]):
        # goal: get financials data for ticker list 
        if tickerList == []:
            tickerList = self.tickers
        tickerObject = Ticker(" ".join(tickerList))
        fundamentals = {"Balance Sheet":tickerObject.balance_sheet(argFreq, argTrailing), "Income Statement":tickerObject.income_statement(argFreq, argTrailing), 
                        "Cash Flow Statement":tickerObject.cash_flow(argFreq, argTrailing), "Valuation":tickerObject.valuation_measures, 
                        "all":tickerObject.all_financial_data(), "get":tickerObject.get_financial_data(metrics, trailing=argTrailing)}[method]
        return fundamentals.reset_index()
