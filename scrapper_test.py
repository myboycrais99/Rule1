"""
This program reads in the financials of a stock from Google Finance. Currently,
this script only reads in the annual data for "income statement",
"balance sheet", and "cash flow". The data are placed into dictionary with the
financial element names as the keys.
"""
from datetime import datetime
import mechanicalsoup
from bs4 import BeautifulSoup
import numpy as np
import http.cookiejar


def make_number(s):
    """
    This function takes in a string and returns either a number if the string is
    a valid representation of a number, nan's for blank entries, and False if
    the string is not a number.

    :param s: string, string to check if a number
    :return: float or False, float if string is a number, False if not
    """
    try:
        float(s)
        return float(s)
    except ValueError:
        if s == "-":
            return np.nan
        else:
            return False


def fetch_webpage(stock_ticker):
    """
    This function takes in a stock symbol/ticker and returns the page content as
    a BeautifulSoup object.

    :param stock_ticker: string, stock symbol/ticker
    :return: BeautifulSoup
    """

    # This string is the root url on Google Finance with the stock ticker the
    # only variable within the string
    url = (r"https://finance.google.com/finance?q={}&fstype=ii"
           "".format(stock_ticker))

    cj = http.cookiejar.CookieJar()
    br = mechanicalsoup.StatefulBrowser()
    br.set_cookiejar(cj)
    return BeautifulSoup(br.open(url).content, "html.parser")


def get_dates(page, tag="thead", date_format="%Y-%m-%d"):
    """
    Takes in a BeautifulSoup object of a page and searches for dates within the
    table. Currently, Google Finance uses dates in the table header so this
    function uses the default "thead" tag to search for a table head. All table
    headers are the same so this function uses the last one in the html. Then
    the function looks for all table head elements "th" and checks to see if
    they end in numbers. If so, read the last set of characters equal to the
    length of date_format. Then use the date_format to generate a datetime
    object.

    :param page: BeautifulSoup Object
    :param tag: string, html tag where dates are stored
    :param date_format: string, format of date string in html
    :return: list of datetime objects
    """

    date_list = list()
    print(page)
    trs = page.find_all(tag)[-1]
    for tds in trs.find_all("th"):
        tmp = str(tds.contents[0]).replace("\n", "")

        # Currently, the date is the last part of the string on Google Fiance
        # and no other elements have the last two characters as numbers.
        if make_number(tmp[-2:]) is not False:
            date_list.append(datetime.strptime(tmp[-10:], date_format))

    return date_list


def get_stock_data(page, dates, annual_table_ids=(
        "incannualdiv", "balannualdiv", "casannualdiv")):
    """
    This function iterates over known table ids ("annual_table_ids") and returns
    the financial elements in a dictionary

    :param page: BeautifulSoup, Google Finance Site
    :param dates: list of datetimes, dates found on website
    :param annual_table_ids: list of strings, known tags for "income statement",
            "balance sheet", and "cash flow"
    :return: dict, dictionary of financial data
    """
    tmp_list = list()
    tmp_list.append("Date")

    num_dates = len(dates)

    for i in dates:
        tmp_list.append(i)

    for cur_id in annual_table_ids:
        tds = page.find(id=cur_id)
        for cont in tds.find_all("td"):

            tmp = cont.contents[len(cont.contents) - 1]

            if "span" in str(tmp):
                tmp = str(cont.find("span").contents[0])

            else:
                tmp = str(tmp)

            tmp = tmp.replace(",", "").replace("\n", "")

            tmp_list.append(tmp)

    tmp_list = np.asanyarray(tmp_list)

    # Manually add entries for ROIC and Free Cash Flow
    for i in ["ROIC", "Free Cash Flow"]:
        tmp_list = np.append(tmp_list, i)
        tmp_list = np.append(tmp_list, np.zeros(shape=(num_dates, ), dtype=int))

    tmp_list = tmp_list.reshape(int(tmp_list.size / int(num_dates + 1)),
                                int(num_dates + 1))

    tmp_dict = dict()
    for i in tmp_list:
        tmp_dict[i[0]] = i[1:]

    tmp_dict["Free Cash Flow"] = \
        tmp_dict["Cash from Operating Activities"].astype(float) + \
        tmp_dict["Capital Expenditures"].astype(float)

    tmp_dict["ROIC"] = (tmp_dict["Net Income"].astype(float) - 0) / (
            tmp_dict["Total Liabilities & Shareholders' Equity"].astype(
                float) - tmp_dict["Total Long Term Debt"].astype(float))

    return tmp_dict


def save_csv(data_dict, filename="google.csv"):
    """
    This function takes in dictionary object, iterates over the contents, and
    saves them into a tab deliminated csv file.

    :param data_dict: dict, dictionary of financial data
    :param filename: string, optional, name of file to save data
    :return: None
    """
    with open(filename, "w") as f:
        for key, val in data_dict.items():
            f.write(key + "\t")
            for i in val:
                f.write(str(i) + "\t")
            f.write("\n")


if __name__ == "__main__":
    ticker = "AAPL"

    page_data = fetch_webpage(ticker)
    stock_dates = get_dates(page_data)

    data = get_stock_data(page_data, stock_dates)

    # save_csv(data)

    from check_table_names import get_valid_website_names

    valid_names = get_valid_website_names()

    names = list()
    for key, val in data.items():
        names.append(key)
        if key in valid_names:
            print(True)
        else:
            print(False, key)

    # print(valid_names)
