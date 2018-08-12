"""
This script parses the html code that was scrapped and saved from investools to
pull out the relevant financial data necessary to calculate the Big 5 from
Rule #1.
"""


from datetime import datetime
from bs4 import BeautifulSoup
import numpy as np

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib.request import urlopen


def open_file(tick, data_str, root=""):
    """This function takes in a stock ticker and the type of financial form
    and returns a beautiful soup object."""
    income_statement = r"{}stock_data/{}_{}.html".format(root, tick, data_str)

    with open(income_statement, 'r') as fil:
        return BeautifulSoup(fil, "html.parser")


def get_stock_data(tick, data_str):
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
            val = [datetime.strptime(x, "%Y %m-%d") for x in val]

        # Otherwise, convert all '-'s to NaNs, remove all commas, and convert
        # the values to floats.
        else:
            val[val == "-"] = 0

            val = [x.replace(",", "") for x in val]

            val = [x.replace("+", "") for x in val]

            for idx, tmp in enumerate(val):
                if tmp[-1] == "%":
                    val[idx] = float(tmp[:-1]) / 100
                else:
                    val[idx] = float(val[idx])

        # Add dictionary key value pair
        stock_data[key] = np.asarray(val)

    return stock_data


def main():
    """The main function"""
    tickers = ["AMZN", "AAPL", "GOOG", "GOOGL"]

    stocks = dict()

    for ticker in tickers[1:2]:
        print(ticker)

        stocks[ticker] = dict(
            list(get_stock_data(ticker, "balance_sheet").items()) +
            list(get_stock_data(ticker, "cash_flow").items()) +
            list(get_stock_data(ticker, "income_statement").items()) +
            list(get_stock_data(ticker, "trend_analysis").items())
        )

        print("\tDate:", [x.year for x in stocks[ticker]["Date"]])

        roic = (
            stocks[ticker]["Operating Income"] * (
                1 - (stocks[ticker]["Income Tax - Total"] /
                     (stocks[ticker]["Net Income Before Taxes"])))) / (
            stocks[ticker]["Total Liabilities"] +
            stocks[ticker]["Common Stock, Total"] +
            stocks[ticker]["Long Term Debt"]
        )
        print("\n\tROIC:", roic)

        print("\n\tSales:", stocks[ticker]["Revenue Total"])

        print("\tSales Growth Rate:",
              stocks[ticker]["Revenue Total"][1:] /
              stocks[ticker]["Revenue Total"][:-1] - 1)

        eps = ((stocks[ticker]["Net Income"] -
               stocks[ticker]["Preferred Dividends"]) /
               stocks[ticker]["Diluted Weighted Average Shares"])
        print("\n\tEPS:", eps)

        print("\tEPS Growth Rate:", eps[1:] / eps[:-1] - 1)

        bvps = (stocks[ticker]["Total Equity"] /
                stocks[ticker]["Total Common Shares Outstanding"])

        print("\n\tEquity:", bvps)

        print("\tEquity Growth Rate:", bvps[1:] / bvps[:-1] - 1)

        print("\n\tCash:", stocks[ticker]["Free Cash Flow"])

        print("\tCash Growth Rate:",
              stocks[ticker]["Free Cash Flow"][1:] /
              stocks[ticker]["Free Cash Flow"][:-1] - 1)

        # save_csv(stocks[ticker])


def save_csv(stock):
    filename = "investools.csv"
    with open(filename, "w") as f:
        for key, val in enumerate(stock):
            f.write(val + "\t")

            for i in stock[val]:
                f.write(str(i) + "\t")
            f.write("\n")


if __name__ == "__main__":
    main()

    # Shiller P/E Ratio
    # http: // www.multpl.com / cpi / table
    # cpi = np.array(
    #     [211.08, 211.14, 216.69, 220.22, 226.67, 230.28, 233.92, 233.71,
    #      236.92, 241.43], dtype=float)
    # data = stocks["AAPL"]["EPS"] / cpi * cpi[-1]
    # print(data, np.mean(data))
