"""
This script uses investools to collect relevant financial data from all public
companies listed in the NASDAQ, NYSE, and AMEX. A temporary account at
investools is required. This script then uses cookies to log in and scrap the
relevant data. The income statements, balance sheets, cash flow, and trend
analysis pages are scraped and saved to the local machine for later analysis.
"""
from __future__ import division, print_function
import mechanize
from bs4 import BeautifulSoup
import numpy as np
import time

try:
    # For Python 3.0 and later
    import http.cookiejar
except ImportError:
    # For Python 3.0 and later
    import cookielib


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
        prop = np.asarray(map(lambda s: s.replace('"', ''),
                              np.genfromtxt(ticker_file.format(
                                  "nasdaq_companylist"), dtype="S32",
                                  skip_header=1, delimiter='",',
                                  comments='##')[:, prop_index]))

        prop = np.append(prop, map(lambda s: s.replace('"', ''),
                                   np.genfromtxt(ticker_file.format(
                                       "nyse_companylist"), dtype="S32",
                                       skip_header=1, delimiter='",',
                                       comments='##')[:, prop_index]))

        # prop = np.append(prop, map(lambda s: s.replace('"', ''),
        #                            np.genfromtxt(ticker_file.format(
        #                                "amex_companylist"), dtype="S32",
        #                                skip_header=1, delimiter='",',
        #                                comments='##')[:, prop_index]))

        return prop


def main():

    site = (r"https://online.investools.com/authentication/auth.iedu?logout="
            "true&brandLogoImage=identifier_investortoolbox")
    site_root = r"https://toolbox.investools.com/graphs/fundamentalAnalysis"
    file_root = r"stock_data\\"

    cj = cookielib.CookieJar()
    br = mechanize.Browser()
    br.set_cookiejar(cj)
    br.open(site)

    br.select_form(nr=0)
    br.form['userid'] = r"rap4yd@gmail.com"
    br.form['password'] = r"WedQ!t^2%ZE79ws"
    br.submit()

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

        income_statement = BeautifulSoup(br.open(site_income_statement).read(),
                                         "html.parser")
        balance_sheet = BeautifulSoup(br.open(site_balance_sheet).read(),
                                      "html.parser")
        cash_flow = BeautifulSoup(br.open(site_cash_flow).read(),
                                  "html.parser")
        trend_analysis = BeautifulSoup(br.open(site_trend_analysis).read(),
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
