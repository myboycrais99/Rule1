"""
This program reads
"""


from bs4 import BeautifulSoup
import requests
import json


# Documentation: https://financialmodelingprep.com/developer/docs

# https://www.barchart.com/stocks/quotes/{ticker}/balance-sheet/annual

# https://research.tdameritrade.com/grid/public/research/stocks/"
#                 "fundamentals/statement/balancesheet?symbol={ticker}

# https://research.tdameritrade.com/grid/public/research/stocks/"
#                 "fundamentals/statement/incomestatement?symbol={ticker}

# https://api.iextrading.com/1.0/stock/{ticker}/financials?period=annual
class Stock:

    def __init__(self, ticker):
        self._ticker = ticker

        # This string is the root url on Financial Modeling Prep with the type
        # of statement and stock ticker to be specified.
        self._url_root = r"https://financialmodelingprep.com/api/financials/"

        # Initialize class variables
        self._income_statement_text = "income-statement"
        self._balance_statement_text = "balance-sheet-statement"
        self._cash_statement_text = "cash-flow-statement"
        self._sales_text = "Revenue"
        self._statement_month = ""
        self._income_statement = dict()
        self._balance_statement = dict()
        self._cash_statement = dict()
        self._eps = dict()
        self._cash_flow = dict()
        self._equity = dict()
        self._shares_out = dict()
        self._bvps = dict()
        self._sales = dict()
        self._total_invest_cap = dict()
        self._net_income = dict()
        self._roic = dict()

        self._net_income_common_text = ("Net income available to common "
                                        "shareholders")
        self._diluted_shares_text = "Diluted"
        self._cash_flow_text = "Net cash provided by operating activities"

        # Get stock data and calculate relevant values
        self._fetch_data()
        self._fetch_shares_outstanding()
        self._fetch_other_balance()
        self._fetch_other_income()
        self._get_statement_month()
        self._calc_eps()
        self._calc_cash_flow()
        self._calc_equity()
        self._calc_bvps()
        self._calc_sales()
        self._calc_roic()

    def _fetch_data(self):
        self._income_statement = json.loads(BeautifulSoup(requests.get(
            self._url_root + self._income_statement_text + r"/{}"
            "".format(self._ticker)).content, "html.parser").text)

        self._balance_statement = json.loads(BeautifulSoup(requests.get(
            self._url_root + self._balance_statement_text + r"/{}"
            "".format(self._ticker)).content, "html.parser").text)

        self._cash_statement = json.loads(BeautifulSoup(requests.get(
            self._url_root + self._cash_statement_text + r"/{}"
            "".format(self._ticker)).content, "html.parser").text)

    def _fetch_shares_outstanding(self):
        # TODO: Need to find more reliable API to get shares outstanding

        link = ("https://www.barchart.com/stocks/quotes/{}/balance-sheet/annual"
                "".format(self._ticker))
        data = BeautifulSoup(requests.get(link).content, "lxml")

        tmp = data.find_all('tr', {'class': ["bc-financial-report__row-dates",
                                             "odd"]})

        dates = list()
        shares = list()
        for i in tmp:
            # print(i)

            if "row-dates" in str(i):
                # print(type(i), i)
                tmp2 = i.find_all("td")
                for j in tmp2[1:]:
                    # print(j.get_text()[4:])
                    dates.append(str(j.get_text()[4:]).strip(" "))

            if "Shares Outstanding, K" in str(i):
                # print(i)
                tmp2 = i.find_all("td")[1:]
                for j in tmp2:
                    tmp3 = str(j.get_text()).strip(" ").replace(",", "")
                    # print(int(dog)*1000)
                    shares.append(int(tmp3)*1000)

        for i in range(len(dates)):
            self._shares_out[dates[i]] = shares[i]

    def _fetch_other_balance(self):
        # TODO: Need to find more reliable API to get total long term debt and equity

        link = ("https://research.tdameritrade.com/grid/public/research/stocks/"
                "fundamentals/statement/balancesheet?symbol={}"
                "".format(self._ticker))
        data = BeautifulSoup(requests.get(link).content, "lxml")

        dates = list()
        tmp = data.find_all("thead", {"class": ["period-header"]})

        for i in tmp[0].find_all("th"):
            tmp2 = str(i.get_text()[:4]).strip(" ")
            if not tmp2 == "":
                dates.append(tmp2)

        tmp = data.find_all("tr", {"id": ["LTTD", "QTLE"]})
        debt = list()
        equity = list()
        for i in tmp:

            if "Total Long Term Debt" in str(i):
                # print(type(i), i)
                for j in i.find_all("td"):
                    debt.append(int(float(str(j.get_text()).strip(
                        " ").replace(",", "")) * 1e6))

            if "Total Equity" in str(i):
                for j in i.find_all("td"):
                    equity.append(int(float(str(j.get_text()).strip(
                        " ").replace(",", "")) * 1e6))

        for i in range(len(dates)):
            self._total_invest_cap[dates[i]] = debt[i] + equity[i]

    def _fetch_other_income(self):
        # TODO: Need to find more reliable API to get net income after tax

        link = ("https://research.tdameritrade.com/grid/public/research/stocks/"
                "fundamentals/statement/incomestatement?symbol={}"
                "".format(self._ticker))
        data = BeautifulSoup(requests.get(link).content, "lxml")

        dates = list()
        tmp = data.find_all("thead", {"class": ["period-header"]})

        for i in tmp[0].find_all("th"):
            tmp2 = str(i.get_text()[:4]).strip(" ")
            if not tmp2 == "":
                dates.append(tmp2)

        tmp = data.find_all("tr", {"id": ["NINC"]})
        net_income = list()
        for i in tmp:

            if "Total Net Income" in str(i):
                # print(type(i), i)
                for j in i.find_all("td"):
                    tmp2 = str(j.get_text()).strip(" ").replace(",", "")

                    if tmp2[0] == "(" and tmp2[-1] == ")":
                        tmp2 = "-" + tmp2[1:-1]

                    net_income.append(int(float(tmp2) * 1e6))

        for i in range(len(dates)):
            self._net_income[dates[i]] = net_income[i]

    def _get_statement_month(self):
        for key, value in self._income_statement[self._ticker][
                self._net_income_common_text].items():

            if not key == "TTM":
                self._statement_month = key[5:]

    def _calc_eps(self):
        for key, value in self._income_statement[self._ticker][
                self._net_income_common_text].items():

            # TODO: Check to see if date already in database. If not, need to add ticker, date (year), and value

            if not key == "TTM":
                self._eps[key[0:4]] = (
                        float(self._income_statement[self._ticker][
                            self._net_income_common_text][key]) /
                        float(self._income_statement[self._ticker][
                            self._diluted_shares_text][key]))

    def _calc_cash_flow(self):
        for key, value in self._balance_statement[self._ticker][
                self._cash_flow_text].items():

            if not key == "TTM":
                self._cash_flow[key[0:4]] = int(int(value)*1e6)

    def _calc_equity(self):
        # TODO: Determine how to calculate equity from balance statement
        # Currently, a second API is used to get equity directly
        tmp_equity = json.loads(BeautifulSoup(requests.get(
            r"https://api.iextrading.com/1.0/stock/{}/financials?period=annual"
            "".format(self._ticker)).content, "html.parser").text)["financials"]

        for i in range(len(tmp_equity)):
            self._equity[tmp_equity[i]["reportDate"][:4]] = int(
                tmp_equity[i]["shareholderEquity"])

    def _calc_bvps(self):
        for key, value in self._equity.items():
            # print(self._equity[key]*1e6 / self._shares_out[key])
            self._bvps[key] = self._equity[key] / self._shares_out[key]

    def _calc_sales(self):
        for key, value in self._income_statement[self._ticker][
                self._sales_text].items():

            if not key == "TTM":
                self._sales[key[0:4]] = int(float(value) * 1e6)

    def _calc_roic(self):
        for key, value in self._net_income.items():
            if not key == "TTM":
                self._roic[key[0:4]] = float(self._net_income[key] /
                                             self._total_invest_cap[key])



    @property
    def ticker(self):
        return self._ticker

    @property
    def statement_month(self):
        return self._statement_month

    @property
    def eps(self):
        return self._eps

    @property
    def cash_flow(self):
        return self._cash_flow

    @property
    def equity(self):
        return self._equity

    @property
    def shares_out(self):
        return self._shares_out

    @property
    def bvps(self):
        return self._bvps

    @property
    def sales(self):
        return self._sales

    @property
    def net_income(self):
        return self._net_income

    @property
    def roic(self):
        return self._roic


if __name__ == "__main__":

    tickers = ["AAPL"]

    # for tick in tickers:
    #
    #     bob = Stock(tick)
    #
    #     print("Ticker: ", bob.ticker)
    #     print("Reporting Month: ", bob.statement_month)
    #     print("EPS: ", bob.eps)
    #     print("Cash Flow: ", bob.cash_flow)
    #     # print("Equity: ", bob.equity)
    #     # print("Shares Out: ", bob.shares_out)
    #     print("BVPS: ", bob.bvps)
    #     print("Sales: ", bob.sales)
    #     # print("Long Debt: ", bob.total_long_debt)
    #     # print("Net Income: ", bob.net_income)
    #     print("ROIC: ", bob.roic)
    #
    #     print("\n\n")

    response = requests.get("https://financialmodelingprep.com/api/financials/income-statement/AAPL")
    #
    # import re
    # data = json.loads(re.sub('<[^<]+?>', '', response.text))
    #
    # print(data)
    print(type(response.text))
