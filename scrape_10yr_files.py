"""
This script parses the html code that was scrapped and saved from investools to
pull out the relevant financial data necessary to calculate the Big 5 from
Rule #1.
"""

from __future__ import division, print_function
from datetime import datetime
from bs4 import BeautifulSoup
from scrape_investools import stock_info
import numpy as np

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen


def open_file(tick, data_str, root=""):
    """This function takes in a stock ticker and the type of financial form
    and returns a beautiful soup object."""
    income_statement = r"{}stock_data/{}_{}.html".format(root, tick, data_str)

    with open(income_statement, 'r') as fil:
        return BeautifulSoup(fil, "html.parser")


def parse_stock_data(tick, data_str):
    """This function opens the 10-year stock data specified by 'data_str' for
    the passed stock ticker. Once open, the function parses the HTML data and
    returns a dictionary with keys taken from the first column of the website
    and the values from the remaining ten columns.
    """
    data = open_file(tick, data_str)

    data_columns = data.find_all('table')[1:]

    values = list()
    stock_data = dict()

    for column in data_columns:

        row = column.find_all('td')

        for hit in row:
            if "span" and "Values in Millions of $" in str(hit):
                values.append("Date")

            else:
                if hit.string is not None:
                    values.append(str(hit.string))

    # The investools website provides ten columns of data regardless of the age
    # of the company. Therefore, number of columns is ten plus title column.
    num_cols = 11
    values = np.asarray(values).reshape(num_cols, int(len(values) / num_cols)).T

    # Loop through the rows of data
    for value in values:

        key, val = value[0].strip(":"), value[1:]

        # Check to see if data is Date row and if so, convert to datetime.
        if key == "Date":
            val = map(lambda x: datetime.strptime(x, "%Y %m-%d"), val)

        # Otherwise, convert all '-'s to NaNs, remove all commas, and convert
        # the values to floats.
        else:
            val[val == "-"] = np.nan

            val = map(lambda x: x.replace(",", ""), val)

            val = map(lambda x: x.replace("+", ""), val)

            for idx, tmp in enumerate(val):
                if tmp[-1] == "%":
                    val[idx] = float(tmp[:-1]) / 100
                else:
                    val[idx] = float(val[idx])

        # Add dictionary key value pair
        stock_data[key] = val

    return stock_data


def main():
    """The main function"""
    # tickers = ["AAPL", "GOOG", "GOOGL"]
    # tickers = tickers[1]

    offset_start = 0
    tickers = stock_info(prop_index=0)[offset_start:3]
    for ticker in tickers[0:1]:
        print(ticker)
        balance_sheet = parse_stock_data(ticker, "balance_sheet")
        cash_flow = parse_stock_data(ticker, "cash_flow")
        income_statement = parse_stock_data(ticker, "income_statement")
        trend_analysis = parse_stock_data(ticker, "trend_analysis")

        print(balance_sheet["Cash"])
        print(cash_flow["Cash Taxes Paid"])
        print(income_statement["Diluted Normalized EPS"])
        print(trend_analysis["EPS"])


if __name__ == "__main__":
    main()
