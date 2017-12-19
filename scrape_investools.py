"""
This script uses investools to collect relevant financial data from all public
companies listed in the NASDAQ, NYSE, and AMEX. A temporary account at
investools is required. This script then uses cookies to log in and scrap the
relevant data. The income statements, balance sheets, cash flow, and trend
analysis pages are scraped and saved to the local machine for later analysis.
"""

import mechanicalsoup
from bs4 import BeautifulSoup
import numpy as np
import time
import http.cookiejar



def get_stock_data(beautiful_soup_result, search_str, root, tick, data_str):
    for txt in beautiful_soup_result:

        if search_str in str(txt):
            data = str(txt)
            filename = r"{}{}_{}.html".format(root, tick, data_str)

            with open(filename, "w") as f:
                f.write(data)

            break


def stock_info(prop_index=0):
    ticker_file = r"tickers\{}.csv"

    prop = np.genfromtxt(ticker_file.format(
        "nasdaq_companylist"), dtype="S32",
        skip_header=1, delimiter='",',
        comments='##')[:, prop_index]

    prop = [s.decode("utf-8") for s in prop]

    prop = np.asarray([s.replace('"', '') for s in prop])

    return prop


def main():

    site = (r"https://online.investools.com/authentication/auth.iedu?logout="
            "true&brandLogoImage=identifier_investortoolbox")
    site_root = r"https://toolbox.investools.com/graphs/fundamentalAnalysis"
    file_root = r"stock_data\\"

    cj = http.cookiejar.CookieJar()
    br = mechanicalsoup.StatefulBrowser()
    br.set_cookiejar(cj)
    br.open(site)

    br.select_form(nr=0)
    br['userid'] = r"rap4yd@gmail.com"
    br['password'] = r"WedQ!t^2%ZE79ws"

    br.submit_selected()

    offset_start = 0
    tickers = stock_info(prop_index=0)[offset_start:3]

    for i, ticker in enumerate(tickers):
        ticker = ticker.strip()
        print("{}, {:05.2f}%, {}".format(i + offset_start, (i + 1) /
                                         tickers.shape[0] * 100, ticker))

        site_income_statement = r"{}.iedu?report=IS&symbol={}".format(site_root,
                                                                      ticker)
        site_balance_sheet = r"{}.iedu?report=BS&symbol={}".format(site_root,
                                                                   ticker)
        site_cash_flow = r"{}.iedu?report=CF&symbol={}".format(site_root,
                                                               ticker)
        site_trend_analysis = r"{}/trendAnalysis.iedu?symbol={}".format(
            site_root, ticker)

        income_statement = BeautifulSoup(br.open(site_income_statement).content,
                                         "html.parser")
        balance_sheet = BeautifulSoup(br.open(site_balance_sheet).content,
                                      "html.parser")
        cash_flow = BeautifulSoup(br.open(site_cash_flow).content,
                                  "html.parser")
        trend_analysis = BeautifulSoup(br.open(site_trend_analysis).content,
                                       "html.parser")

        search_string = "Values in Millions of $"

        get_stock_data(income_statement.find_all('table'), search_string,
                       file_root, ticker, data_str="income_statement")
        get_stock_data(balance_sheet.find_all('table'), search_string,
                       file_root, ticker, data_str="balance_sheet")
        get_stock_data(cash_flow.find_all('table'), search_string, file_root,
                       ticker, data_str="cash_flow")
        get_stock_data(trend_analysis.find_all('table'), "Period Ending:",
                       file_root, ticker, data_str="trend_analysis")

        time.sleep(0.1)


if __name__ == "__main__":
    main()
