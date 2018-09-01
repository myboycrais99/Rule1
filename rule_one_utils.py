"""
This file contains multiple utility classes used for the Rule 1 investing
program.
"""

from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import datetime
import json
import numpy as np
import re
import requests
from selenium import webdriver

import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('RuleOneLogger')


class GenericInterface(ABC):
    """
    This abstract class provides abstract methods for fetching and processing
    data from any source. When instantiated, the contained methods should be
    overwritten to fetch data from a particular source and process that data to
    return a useful data set.
    """

    def __init__(self, ticker: str):
        self._ticker = ticker
        super().__init__()

        self._data = None

    @abstractmethod
    def _fetch_data(self):
        """
        This method fetches data from a source. Can be customized based on
        particular API or system specific requirements.
        :return: None
        """

    @abstractmethod
    def _process_data(self):
        """
        This method processes the data returned from "fetch_data" and returns a
        useful data set.
        :return: None
        """

    @property
    def ticker(self):
        return self._ticker


class FetchHTML(GenericInterface):
    """
    Implementation of the GenericInterface specifically tailored for sraping
    HTML sites. The process_data method needs to be customized to fit the
    specific site being scraped.
    """
    def __init__(self, ticker):
        super().__init__(ticker)

        self._url = ""
        self._response = None
        self._data = dict()
        self._status_code = -1

    def __str__(self):
        return str(self._status_code)

    def _fetch_data(self):
        """ Retrieves html code from the specified url and ticker """

        logger.info("Attempting to fetch HTML data from {} for ticker {}"
                    "".format(self._url.split(".com")[0] + ".com",
                              self._ticker))

        tmp_response = requests.get(self._url)
        self._status_code = tmp_response.status_code

        # Log the response
        if tmp_response.status_code == 200:
            logger.info("Ticker {} found at {}"
                        "".format(self._ticker,
                                  self._url.split(".com")[0] + ".com"))

            # self._html = tmp_response.content
            self._response = tmp_response
            self._process_data()

        else:
            logger.warning("Ticker {} not found at {}"
                           "".format(self._ticker,
                                     self._url.split(".com")[0] + ".com"))

    def _process_data(self):
        pass


class FetchHTMLwithJavascript(GenericInterface):
    """
    Implementation of the GenericInterface specifically tailored for sraping
    sites that use Javascript to render HTML using Selenium and the Chrome
    browser driver. This is a very expensive class and very slow. Only use if
    the Javascript must be processed to get the required data.

    The process_data method needs to be customized to fit the specific site
    being scraped.
    """
    def __init__(self, ticker):
        super().__init__(ticker)

        self._url = ""
        # self._response = None
        self._data = dict()
        self._status_code = -1

        options = webdriver.ChromeOptions()
        options.headless = True
        self._driver = webdriver.Chrome(chrome_options=options)

    def __str__(self):
        return str(self._status_code)

    def _fetch_data(self):
        """
        Uses selenium and a headless Google Chrome browser to retrieve html
        code from the specified url and ticker.
        """

        logger.info("Attempting to fetch HTML data from {} for ticker {}"
                    "".format(self._url.split(".com")[0] + ".com",
                              self._ticker))

        self._driver.get(self._url)

        # Selenium does not currently provide a status code for page returns. If
        # the provided url and the resulting url query are the same, assume that
        # the provided url exists and a page was found. If a redirect happens,
        # this could be due to the site updating a link or that the provided url
        # does not exist. For this code, assume the latter.
        if self._driver.current_url == self._url:
            self._status_code = 200
            logger.info("Ticker {} found at {}".format(
                self._ticker, self._url.split(".com")[0] + ".com"))
            self._html = self._driver.page_source
            self._process_data()
        else:
            self._status_code = 404
            logger.warning("Ticker {} not found at {}".format(
                self._ticker, self._url.split(".com")[0] + ".com"))

    def _process_data(self):
        pass


class ScrapeBarchartBalanceSheetHTML(FetchHTML):
    """
    This class scrapes the HTML from the balance sheet data on Barchart.com to
    get values required to calculate the Big Five numbers from Rule 1.

    :param: ticker : str
        Ticker symbol of a stock

    :param: status_code : int
        Status code of HTML query.
            200 : Successful
            500 : Unsuccessful

    :param: dates : list
        Dates for which data were retrieved

    :param: report_month : int
        Month in which the annual report is generated

    :param: data : dict
        Dictionary of data generated from HTML code

    :return: None

    Usage: ScrapeBarchartBalanceSheetHTML("AAPL")
           data = ScrapeBarchartBalanceSheetHTML("AAPL").data

    Note: Currently this is only used to get the shares outstanding needed to
    calculate book value per share.
    """

    def __init__(self, ticker: str):
        super().__init__(ticker)
        self._url = ("https://www.barchart.com/stocks/quotes/{}"
                     "/balance-sheet/annual".format(self._ticker))
        self._dates = list()
        self._report_month = 0

        self._fetch_data()

    def _process_data(self):
        """
        This method uses BeautifulSoup to parse through the HTML to find
        specific values of interest and returns a dictionary with keys specified
        by the strings used on the website. Dictionary values are themselves
        dictionaries with year as the key.
        """
        data = BeautifulSoup(self._response.content, "html.parser")

        # All stock data are contained within <tr> tags. Currently, only stock
        # are in <tr> tags. Use BeautifulSoup to return only data in <tr> tags.
        trs = data.find_all("tr")

        # Loop through all found <tr> tags. If none are found, this block of
        # code is skipped and a warning message is added to the log as a result.
        for ii in trs:
            # Within all rows, there are six values: title and five years of
            # data. The data text within a table row are separated by two or
            # more spaces. Split the table row if two spaces are
            # encountered.
            tmp_list = ii.text.split("  ")

            # The table row containing dates has the keyword "dates" in the
            # table row class. If "dates" is found in the string, assume the
            # table data are dates in the format MM-YYYY.
            if "dates" in str(ii):

                for jj in tmp_list:

                    # If the field matches the MM-YYYY format, append the year
                    # to dates. Otherwise, ignore the value.
                    try:
                        self._dates.append(datetime.datetime.strptime(
                            jj.strip(" "), '%m-%Y').year)
                    except ValueError:
                        pass

                # Get the statement month from the date string
                try:
                    self._report_month = datetime.datetime.strptime(
                        tmp_list[1].strip(" "), '%m-%Y').month
                except ValueError:
                    pass

            # Rows containing data should have six or more entries. Rows with
            # fewer values are header rows.
            elif len(tmp_list) >= 6:
                # Occasional rows have empty strings in the first and/or last
                # position in the list.
                if tmp_list[0] == "":
                    tmp_list = tmp_list[1:]
                if tmp_list[-1] == "":
                    tmp_list = tmp_list[:-1]

                # Create a temporary dictionary to hold date-value information
                # for the current row key.
                tmp_dict = dict()
                for idx, kk in enumerate(tmp_list):
                    # Remove leading or trailing spaces
                    tmp_list[idx] = kk.lstrip().rstrip()

                    # The first value in the list is the name of the data
                    # (e.g., "equity"). Pair the remaining data with the correct
                    # date and add to temporary dictionary. Strip dollar signs
                    # and commas from the entry.
                    #
                    # All values are presented in thousands of dollars
                    if idx > 0:
                        tmp_dict[self._dates[idx-1]] = float(
                            tmp_list[idx].replace("$", "").replace(
                                ",", "")) * 1000

                # Store date-value data in data dictionary with the name as the
                # key.
                self._data[tmp_list[0]] = tmp_dict

        if bool(self._data):
            logger.info("{} data retrieved for {} from Barchart.com"
                        "".format("Balance-sheet", self._ticker))
        else:
            logger.warning("Failed to retrieve {} data for {} from Barchart.com"
                           "".format("Balance-sheet", self._ticker))

    @property
    def data(self):
        return self._data

    @property
    def dates(self):
        return self._dates

    @property
    def status_code(self):
        return self._status_code

    @property
    def report_month(self):
        return self._report_month


class ScrapeTDAmeritradeHTML(FetchHTMLwithJavascript):
    """
    This class scrapes the HTML data on from TDAmeritrade.com to get values
    required to calculate the Big Five numbers from Rule 1. Currently
    TDAmeritrade is only used to calculate ROIC. The balance sheet is used to
    get Total Long Term Debt and Total Equity and the income statement is used
    to get the Net Income.

    TDAmeritrade uses javascript to render the page and also requires sessions.
    Use Selenium and Chrome to render the page content using the ticker symbol
    and then navigate to secondary links using the browser session to get to the
    desired data.

    :param: ticker : str
        Ticker symbol of a stock

    :param: status_code : int
        Status code of HTML query.
            200 : Successful
            500 : Unsuccessful

    :param: dates : list
        Dates for which data were retrieved

    :param: report_month : int
        Month in which the annual report is generated

    :param: data : dict
        Dictionary of data generated from HTML code

    :return: None

    Usage: ScrapeTDAmeritradeHTML("AAPL")
           data = ScrapeTDAmeritradeHTML("AAPL").data

    Note: Currently this is only used to get the shares outstanding needed to
    calculate book value per share.
    """

    def __init__(self, ticker: str):
        super().__init__(ticker)
        # First url is landing point for fundamentals for the specified ticker
        self._url = (r"https://research.tdameritrade.com/grid/public/research/"
                     "stocks/fundamentals?symbol={}".format(self._ticker))

        # Second url is the link embedded in the HTML returned from the previous
        # url. Following this link yields the balance sheet annual data.
        self._url_next = (r"https://research.tdameritrade.com/grid/public/"
                          "research/stocks/fundamentals/statement/"
                          "incomestatement?period=A")
        self._dates = list()
        self._report_month = 0

        self._fetch_data()

        # To get income statement next, update the url_next attribute and re-run
        # the process_data method.
        self._url_next = (r"https://research.tdameritrade.com/grid/public/"
                          "research/stocks/fundamentals/statement/balancesheet"
                          "?period=A")

        self._process_data()
        self._driver.quit()

    def _process_data(self):
        """
        This method uses BeautifulSoup to parse through the HTML to find
        specific values of interest and returns a dictionary with keys specified
        by the strings used on the website. Dictionary values are themselves
        dictionaries with year as the key.
        """

        # To get to annual balance sheet and income statement data from the
        # fundamentals landing page, the webdriver needs to follow the
        # appropriate link and render the new HTML content.
        self._driver.get(self._url_next)
        self._html = self._driver.page_source

        data = BeautifulSoup(self._html, "html.parser")

        # All stock data are contained within <tr> tags. Currently, only stock
        # are in <tr> tags. Use BeautifulSoup to return only data in <tr> tags.
        tables = data.find_all("table")

        # If dates list is empty, extract the dates from the page. Dates are
        # repeated as table headers (<thead>) in every <table> tag that contains
        # the desired data with the class "period-header". Dates are extracted
        # from each <th> tag with the date format YYYYmm/dd/yy.
        if not bool(self._dates):
            dates = tables[1].find("thead", {"class": ["period-header"]})
            for ii in dates.find_all("th"):
                if not ii.text == "":
                    self._dates.append(datetime.datetime.strptime(
                        ii.text, "%Y%m/%d/%y").year)
            self._report_month = datetime.datetime.strptime(
                dates.find_all("th")[-1].text, "%Y%m/%d/%y").month

        multiplier = list()
        headers = data.find_all("h3", {"class": "section-header"})
        for ii in headers:
            if "thousand" in ii.text.lower():
                multiplier.append(1e3)
            elif "million" in ii.text.lower():
                multiplier.append(1e6)
            elif "billion" in ii.text.lower():
                multiplier.append(1e9)
            elif "trillion" in ii.text.lower():
                multiplier.append(1e12)
            else:
                logger.error("No multiplier found for ticker {} on balance"
                             "sheet".format(self._ticker))
                self._data = {}
                return None

        # As of 31AUG18, there are four <table>s currently on the TDAmeritrade
        # balance sheet site and fourteen <table>s on the income statement. In
        # both cases, the first <table> is only a header with daily info. Sort
        # through all other tables to get stock data.
        for idx, ii in enumerate(tables[1:]):

            # Search for table rows <tr>s for each row entry
            trs = ii.find_all("tr")
            for jj in trs[1:]:

                # Field name stored between only <th> tag in the table row
                tmp_field = jj.find("th").text

                # Temporary dictionary to capture each row of data in
                # year: value pairs. Reset each loop.
                tmp_dict = dict()

                # Data are stored between <td> tags. Loop through each <td>
                # field and remove undesired characters.
                for idx2, kk in enumerate(jj.find_all("td")):

                    try:
                        tmp_val = kk.text.replace(
                            ",", "").replace(
                            "(", "-").replace(
                            ")", "").replace(
                            "--", "0")

                        # Multiply values by the multiplier identified in the
                        # table with the exception of EPS values.
                        if " eps" in tmp_field.lower():
                            tmp_val = float(tmp_val)
                        else:
                            tmp_val = float(tmp_val) * multiplier[idx]

                        tmp_dict[self._dates[idx2]] = tmp_val

                    except ValueError:
                        logger.error("Failed to get {} for {}".format(
                            tmp_field, self._ticker))

                # Add each temporary dictionary to the data set to be returned.
                self._data[tmp_field] = tmp_dict

        # Log the success or failure of retrieving the data.
        url_str = "unknown"
        if "balancesheet" in self._url_next:
            url_str = "Balance sheet"
        elif "incomestatement" in self._url_next:
            url_str = "Income statement"
        elif "cashflow" in self._url_next:
            url_str = "Cash flow"

        if bool(self._data):
            logger.info("{} data retrieved for {} from {}".format(
                url_str, self._ticker, self._url.split(".com")[0] + ".com"))
        else:
            logger.warning("Failed to retrieve {} data for {} from {}".format(
                url_str, self._ticker, self._url.split(".com")[0] + ".com"))

    @property
    def data(self):
        return self._data

    @property
    def dates(self):
        return self._dates

    @property
    def status_code(self):
        return self._status_code

    @property
    def report_month(self):
        return self._report_month


class ScrapeIEXTradingFinancialsJSON(FetchHTML):
    """
    This class scrapes the JSON from API provided by IEXTrading.com to
    get values required to calculate shareholder equity Big Five number
    from Rule 1.

    :param: ticker : str
        Ticker symbol of a stock

    :param: status_code : int
        Status code of JSON query.
            200 : Successful
            500 : Unsuccessful

    :param: dates : list
        Dates for which data were retrieved

    :param: report_month : int
        Month in which the annual report is generated

    :param: data : dict
        Dictionary of data generated from JSON code

    :return: None

    Usage: ScrapeIEXTradingJSON("AAPL")
           data = ScrapeIEXTradingJSON("AAPL").data

    Note: Currently this is only used to get the shareholder equity.
    """

    def __init__(self, ticker: str):
        super().__init__(ticker)
        self._url = ("https://api.iextrading.com/1.0/stock/{}/financials"
                     "?period=annual".format(self._ticker))
        self._dates = list()
        self._report_month = 0

        self._fetch_data()

    def _process_data(self):

        # Strip HTML tags from JSON response
        data = json.loads(re.sub('<[^<]+?>', '', requests.get(self._url).text))

        # All data are under the "financial" key at the top level JSON structure
        tmp_date = None
        for ii in data["financials"]:

            # Get date information first.
            tmp_date = datetime.datetime.strptime(ii["reportDate"], "%Y-%m-%d")
            tmp_year = tmp_date.year

            for key, value in ii.items():
                if not key == "reportDate":
                    try:
                        if value is None:
                            value = np.NaN
                        self._data[key][tmp_year] = float(value)
                    except KeyError:
                        self._data[key] = {tmp_year: float(value)}
                    except TypeError:
                        logger.error("TypeError occurred with ticker {} on "
                                     "IEXTrading.com for key {}"
                                     "".format(self._ticker, key))

        self._report_month = tmp_date.month

        # Log if data were successfully retrieved.
        if bool(self._data):
            logger.info("JSON data retrieved for {} from {}".format(
                self._ticker, self._url.split(".com")[0] + ".com"))
        else:
            logger.warning("Failed to retrieve JSON data for {} from {}".format(
                self._ticker, self._url.split(".com")[0] + ".com"))

    @property
    def data(self):
        return self._data

    @property
    def dates(self):
        return self._dates

    @property
    def status_code(self):
        return self._status_code

    @property
    def report_month(self):
        return self._report_month


class ScrapeFinancialModelingPrepJSON(FetchHTML):
    """
    This class scrapes the JSON from API provided by FinancialModelingPrep.com
    to get values required to calculate Sales, EPS, and Cash Flow Big Five
    numbers from Rule 1.

    :param: ticker : str
        Ticker symbol of a stock

    :param: status_code : int
        Status code of JSON query.
            200 : Successful
            500 : Unsuccessful

    :param: dates : list
        Dates for which data were retrieved

    :param: report_month : int
        Month in which the annual report is generated

    :param: data : dict
        Dictionary of data generated from JSON code

    :return: None

    Usage: ScrapeFinancialModelingPrepJSON("AAPL")
           data = ScrapeFinancialModelingPrepJSON("AAPL").data

    Note: Currently this is only used to get the shareholder equity.
    """

    def __init__(self, ticker: str):
        super().__init__(ticker)
        self._url = (r"https://financialmodelingprep.com/api/financials/"
                     r"income-statement/{}".format(self._ticker))
        self._dates = list()
        self._report_month = 0

        self._fetch_data()

        self._url = (r"https://financialmodelingprep.com/api/financials/"
                     r"balance-sheet-statement/{}".format(self._ticker))
        self._fetch_data()

        # Currently income statement and cash flow statements return the same
        # dataset.
        # self._url = (r"https://financialmodelingprep.com/api/financials/"
        #              r"cash-flow-statement/{}".format(self._ticker))
        # self._fetch_data()

    def _process_data(self):

        # Strip HTML tags from JSON response
        data = json.loads(re.sub('<[^<]+?>', '', requests.get(self._url).text))

        # The primary key at the top level JSON structure is the stock ticker
        tmp_date = None

        # Log the success or failure of retrieving the data.
        url_str = "unknown"
        if "balance-sheet" in self._url:
            url_str = "Balance sheet"
        elif "income-statement" in self._url:
            url_str = "Income statement"
        elif "cash-flow" in self._url:
            url_str = "Cash flow"

        if bool(data[self._ticker].values()):

            for key, value in data[self._ticker].items():
                for k, v in value.items():
                    try:
                        tmp_date = datetime.datetime.strptime(k, "%Y-%m")
                        tmp_year = tmp_date.year

                        try:
                            try:
                                v = float(v) * 1e6
                            except ValueError:
                                v = np.NaN
                            self._data[key][tmp_year] = v
                        except KeyError:
                            self._data[key] = {tmp_year: v}
                    except ValueError:
                        pass

                self._report_month = tmp_date.month

            # Log if data were successfully retrieved.
            logger.info("{} data retrieved for {} from {}".format(
                url_str, self._ticker, self._url.split(".com")[0] + ".com"))
        else:
            logger.warning("Failed to retrieve {} data for {} from {}".format(
                url_str, self._ticker, self._url.split(".com")[0] + ".com"))

    @property
    def data(self):
        return self._data

    @property
    def dates(self):
        return self._dates

    @property
    def status_code(self):
        return self._status_code

    @property
    def report_month(self):
        return self._report_month


if __name__ == "__main__":
    pass
