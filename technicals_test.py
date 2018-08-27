"""
This program reads
"""
from datetime import datetime
import mechanicalsoup
from bs4 import BeautifulSoup
import requests
import numpy as np
import http.cookiejar
import json


# Documentation: https://www.alphavantage.co/documentation/
my_token = "SD10CICEOP20YHET"

stock_ticker = "AAPL"

# This string is the root url on Google Finance with the stock ticker the
# only variable within the string

# https://www.alphavantage.co/query?function=MACD&symbol=AAPL&interval=daily&series_type=close&fastperiod=8&slowperiod=17&signalperiod=9&apikey=SD10CICEOP20YHET
url = (r"https://www.alphavantage.co/query?function=MACD"
       "&symbol={}"
       "&interval=daily"
       "&series_type=close"
       "&fastperiod=8"
       "&slowperiod=17"
       "&signalperiod=9"
       "&apikey={}"
       "".format(stock_ticker, my_token))

# bob = BeautifulSoup(requests.get(url).content, "html.parser")

# json_string = json.dumps(bob)

bob = json.loads(requests.get(url).text)

print(bob.keys())

print(bob['Technical Analysis: MACD'].keys())