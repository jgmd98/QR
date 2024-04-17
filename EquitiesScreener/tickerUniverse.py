import pandas as pd
import urllib.request

# get ticker list from nasdaq data using FTP - if it fails use the last ticker list
try:
    local_filename, headers = urllib.request.urlretrieve("ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt")
    tickerData = pd.read_csv(local_filename, sep="|").dropna()
    tickerList = list(tickerData["Symbol"].unique())
    local_filename_other, headers_other = urllib.request.urlretrieve("ftp://ftp.nasdaqtrader.com/symboldirectory/otherlisted.txt")
    tickerData_other = pd.read_csv(local_filename_other, sep="|").dropna()
    tickerList_other = list(tickerData_other["NASDAQ Symbol"].unique())
    tickerList += tickerList_other
    tickerData.to_csv("tickerList.csv")
except:
    print("Nasdaq FTP failed")
    tickerList = list(pd.read_csv("tickerList.csv")["Symbol"].unique())

tickerList = sorted(tickerList)
