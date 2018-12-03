"""
This file contains multiple utility classes used for the Rule 1 investing
program.
"""

from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import csv
import datetime
import glob
import json
import logging.config
# from math import isclose
from multiprocessing.dummy import Pool as ThreadPool
import numpy as np
import os
import re
import requests
import selenium
from selenium import webdriver
import time

# TODO - Add assert statements to Scraper classes (others?)


def function_to_multithread(the_func, to_iterate: list,
                            num_workers: (None, int)=None):
    """

    Parameters
    ----------
        :param function the_func: A function that can be mapped and takes a
            single value or list as an input
        :param to_iterate: Variables to pass into function.
        :param num_workers: Optional, the number of worker threads to spawn.
            Default is to use len(to_iterate) to spawn a thread for each input
            to the function.

    Returns
    -------
        :return list, float: first object returned is a list of outputs from the
            function that is multithreaded. The second object is the time
            elapsed to run the multithreaded function in seconds.
    """
    # make the Pool of workers
    if num_workers is None:
        workers = len(to_iterate)
    else:
        workers = num_workers
    pool = ThreadPool(workers)

    start_time = time.time()

    # Use map function to assign the function to the pool of worker threads
    results = pool.map(the_func, to_iterate)

    # Gather all threads and wait for them to end.
    pool.close()
    pool.join()

    elapsed = time.time() - start_time

    return results, elapsed


class RuleOneLogger(object):
    """Create a custom logger based on the logging class.

    By default, this class uses the "logging.conf" for the configuration file
    that defines the logging options. The config file must either be in the same
    directory as this class or the file and path must be provided in
    "config_file". This class also uses the custom defined "RuleOneLogger"
    logger defined in logging.conf.

    Parameters
    ----------
        :param str config_file: location and name of custom configuration file
            to configure the logging class.

        :param str my_logger: Name of logger to implement. Default for Rule1 is
            "RuleOneLogger" or "root" for logging.Logger class. my_logger should
            be defined in the "config_file".

    Attributes
    ----------
    """

    def __init__(self, config_file: str="logging.conf",
                 my_logger: str="RuleOneLogger"):
        logging.config.fileConfig(config_file)
        self._logger = logging.getLogger(my_logger)

    @property
    def logger(self):
        """
        logging.Logger: Implementation of the logging class using the specified
            or default configuration file.
        """
        return self._logger


class GenericInterface(ABC):
    """Abstract class for fetching and processing data from external source.

    This abstract class provides abstract methods for fetching and processing
    data from any source. When instantiated, the contained methods should be
    overwritten to fetch data from a particular source and process that data to
    return a useful data set.

    Parameters
    ----------

    Attributes
    ----------

    """
    def __init__(self):
        self._response = ""
        self._status_code = 404

    @abstractmethod
    def _fetch_data(self):
        """
        This method fetches data from a source. Can be customized based on
        particular API or system specific requirements.

        Returns
        -------
        :return: None
        """

    @abstractmethod
    def _process_data(self):
        """
        This method processes the data returned from "fetch_data" and returns a
        useful data set.

        Returns
        -------
        :return: None
        """

    @property
    def status_code(self):
        """
        int: Status code of HTML query. Listed are the current valid values and
             their corresponding meaning.

             200 : OK - Page Loaded Successfully
             301 : Redirect - Moved Permanently
             302 : Redirect - Found (Moved Temporary)
             400 : Bad Request
             401 : Unauthorized
             403 : Forbidden
             404 : Page not found
             500 : Internal Server Error
        """
        return self._status_code


class FetchHTML(GenericInterface):
    """Scrapes web page HTML code for processing.

    Implementation of the GenericInterface specifically tailored for sraping
    HTML sites. Class overrides the _fetch_data method to use the requests
    library. The process_data method needs to be customized to fit the specific
    implementation site being scraped.

    Parameters
    ----------
        :param str url: The url of the site to be fetched

    Attributes
    ----------
    """
    def __init__(self, url):
        GenericInterface.__init__(self)

        # Verify that the ticker is of type 'str' before continuing. If not, log
        # the error and set the status_code to 404 to indicate a bad web
        # response.
        self._url = None
        try:
            assert isinstance(url, str)
            self._url = url
        except AssertionError:
            logger.error("Expect type 'str' for url, got {} for url {}"
                         "".format(type(url), url))
            self._status_code = 404

    def __str__(self):
        return str(self._status_code)

    def _fetch_data(self):
        """Retrieves html code from the specified url.

        Uses the requests package to retrieve HTML code from the provided url.
        Checks the response status code to verify that the page was found and
        data was retrieved.

        Parameters
        ----------

        Attributes
        ----------

        Returns
        -------

        """

        logger.debug("Attempting to fetch HTML data from {}".format(self._url))

        # Confirm that the web page returned a good status code before
        # proceeding or log an error. An error results in _response staying the
        # default value of an empty string. Set allow_redirect flag to false to
        # prevent site fom redirecting a bad url to new page as this renders bad
        # data for parsing. Can also implement the requests.history parameter to
        # capture redirects.
        tmp_response = requests.get(self._url, allow_redirects=False)
        self._status_code = tmp_response.status_code
        if tmp_response.status_code == 200:
            logger.debug("Data successfully retrieved from {}"
                         "".format(self._url))

            self._response = tmp_response.content.decode("utf-8")

        else:
            logger.error("Failed to retrieve data from {}".format(self._url))
            self._response = ""

    def _process_data(self):
        pass


class FetchHTMLwithJavascript(FetchHTML):
    """Scrapes web pages that use javascript to render content.

    Implementation of the GenericInterface specifically tailored for sraping
    sites that use Javascript to render HTML using Selenium and the Chrome
    browser driver. This is a very expensive class and very slow. Only use if
    the Javascript must be processed to get the required data.

    The process_data method needs to be customized to fit the specific site
    being scraped.

    Parameters
    ----------
        :param str url: The url of the site to be fetched

    Returns
    -------

    """
    def __init__(self, url):
        FetchHTML.__init__(self, url)

        options = webdriver.ChromeOptions()
        options.headless = True
        self._driver = webdriver.Chrome(options=options)
        self._driver.set_page_load_timeout(10)

    def __del__(self):
        try:
            self._driver.quit()
        except ImportError:
            pass

    def _fetch_data(self):
        """Use selenium and Chrome driver to render dynamic javascript content.

        Uses selenium and a headless Google Chrome browser to retrieve html
        code from the specified url. After generating the headless driver, this
        class will retrieve the data specified by the site. However, if a bad
        url is provided selenium still returns a good status message if any HTML
        code is returned. Class checks that the url specified by the driver
        after fetching the page is the same url that was originally specified.

        Additionally, no public attributes or getters are defined for this
        class.

        Parameters
        ----------

        Attributes
        ----------

        Returns
        -------

        """

        logger.debug("Attempting to fetch HTML data from {}".format(self._url))

        self._driver.get(self._url)

        # Selenium does not currently provide a status code for page returns. If
        # the provided url and the resulting url query are the same, assume that
        # the provided url exists and a page was found. If a redirect happens,
        # this could be due to the site updating a link or that the provided url
        # does not exist. For this code, assume the latter.
        if self._driver.current_url == self._url:
            self._status_code = 200

            logger.debug("Data successfully retrieved from {}"
                         "".format(self._url))

        else:
            self._status_code = 404
            logger.warning("Failed to retrieve data from {}".format(self._url))
            self._driver.quit()

    def _process_data(self):
        pass


class StockScrapper(ABC):
    """Abstract class for Scraper classes used to scrape stock data.

    This class provides an the structure necessary for handling data relevant to
    stock sites. This includes multiple getter functions that serve as an
    interface to the data generated by the subclass. No public attributes are
    defined for this class.

    Additionally, this class checks the ticker to ensure that it
    has the correct type.

    TODO - Add check for ticker against known tickers to reduce unnecessary
           computations

    Parameters
    ----------
        :param str ticker: Stock ticker

    Attributes
    ----------

    """
    def __init__(self, ticker: str, statements: (list, str)=""):

        self._ticker = None
        try:
            assert isinstance(ticker, str)
            self._ticker = ticker
        except AssertionError as e:
            logger.error("Expect type 'str' for ticker, got {} for ticker {}"
                         "".format(type(ticker), ticker))
            raise e

        try:
            assert isinstance(statements, (list, str))
            if isinstance(statements, str):
                assert statements in ["income", "balance", "cash"]
            else:
                for i in statements:
                    assert i in ["income", "balance", "cash"]
        except AssertionError as e:
            logger.error("Expect type 'str' or 'list' for statements, got {} "
                         "for ticker {}.".format(type(ticker), ticker))
            raise e

        self._data = dict()
        self._dates = list()
        self._report_month = int

    def _log_bad_value(self, source: str, got: str, field: str) -> None:
        """Creates log message when non-numeric value is found for stock data.

        This function is called when converting a data value to a numeric
        returns a ValueError exception. The function takes in the relevant url
        and data parameters and constructs a standardized error message for
        logging. The log type is "warning" for this error as bad data types are
        expected.

        Parameters
        ----------
            :param str source: Source of data that provided a non-numeric value

            :param str got: The value provided by the source

            :param str field: Name of financial field that had a bad value
                (e.g., "Net Income")

        Returns
        -------

        """
        logger.warning(
            "Got bad value for {} at {}. Got '{}' for field '{}'"
            "".format(self._ticker, source, got, field))

    def _get_dates(self, data: BeautifulSoup, search_str: str,
                   wrapper_tag: str, date_format: str):
        """Search through Beautifulsoup data for stock dates.

        This method takes in a Beautifulsoup object and uses the provided search
        parameters to identify dates in the HTML and then parse the dates using
        the provided date format.

        Parameters
        ----------
            :param data: Beautifulsoup object
            :param search_str: Unique identifying string of text used in HTML to
                identify dates. Typically a class name.
            :param wrapper_tag: HTML tag used to wrap each date entry.
            :param date_format: Representation of date in datetime format.

        Returns
        -------

        """
        try:
            values_list = list(
                filter(None, map(lambda x: x.text.strip(), data.select_one(
                    search_str).find_all(wrapper_tag))))

            self._dates = list(map(
                lambda x: datetime.datetime.strptime(
                    x.strip(), date_format).year, values_list))

            self._report_month = datetime.datetime.strptime(
                values_list[0].strip(), date_format).month
        except AttributeError:
            logger.error("Error getting date for {} from Barchart.com"
                         "".format(self._ticker))

    @staticmethod
    def _multiple_replace(old_str: str, rep: dict) -> str:
        """Bulk replace multiple strings in a single string.

        This function takes in a dictionary of strings and replaces any instance
        of these strings found within a given string. Useful for removing
        multiple bad characters in a string to then convert to numeric values.

        Parameters
        ----------
            :param str old_str: String to search through for bad character
            :param dict rep: Dictionary of strings to replace

        Returns
        -------
            :return str: String purged of substrings defined by rep
        """
        rep = dict((re.escape(k), v) for k, v in rep.items())
        pattern = re.compile("|".join(rep.keys()))

        return pattern.sub(lambda m: rep[re.escape(m.group(0))], old_str)

    @staticmethod
    def _make_num(string: str, new_type: type = float()):
        """Convert string to user defined numeric type.

        This function attempts to converts an object of type <str> to a user
        defined numeric type. If the string cannot be converted to a numeric
        type, a numpy.NaN is returned.

        Parameters
        ----------
            :param str string: The string to be converted to a number
            :param object new_type: The object type to convert the string to
                (e.g., float, int). Default is float.

        Returns
        -------
            :return: Numeric conversion of string
        """
        try:
            return new_type(string)
        except ValueError:
            return np.NaN

    @property
    def ticker(self):
        """
        str: The ticker corresponding to the stock for which data are to be
             retrieved
        """
        return self._ticker

    @property
    def data(self):
        """
        dict: Dictionary containing the processed stock data. All classes
              implementing this interface will obey the following convention:
              data[param_name][year] = value
        """
        return self._data

    @property
    def dates(self):
        """
        list: Dates corresponding to the data extracted. Used as keys for the
              data dictionary.
        """
        return self._dates

    @property
    def report_month(self):
        """
        int: The integer month that the financial reports for the stock are
             released
        """
        return self._report_month


class ScrapeBarchartHTML(FetchHTML, StockScrapper):
    """Scrapes HTML data from Barchart.com.

    This class scrapes the HTML from the balance sheet and income statement data
    on Barchart.com to get values required to calculate the Big Five numbers
    from Rule 1.

    Note
    ----
        Currently this is only used to get the shares outstanding needed to
        calculate book value per share.

    Parameters
    ----------
        :param: ticker : str
            Ticker symbol of a stock

    Attributes
    ----------

    Examples
    --------
        ScrapeBarchartHTML("AAPL")
        data = ScrapeBarchartHTML("AAPL").data

        Interface Definition:
            data[param_name][year] = value
    """

    def __init__(self, ticker: str):
        StockScrapper.__init__(self, ticker)
        FetchHTML.__init__(self, "https://www.barchart.com/stocks/quotes/{}/"
                                 "balance-sheet/annual".format(self._ticker))

        # Check to ensure the _ticker and _url are defined. If both exist, fetch
        # HTML code
        if self._ticker is not None and self._url is not None:
            self._fetch_data()

        # Verify a good status code was received before processing the HTML data
        if self.status_code == 200:
            self._process_data()

        self._url = ("https://www.barchart.com/stocks/quotes/{}/"
                     "income-statement/annual".format(self._ticker))

        if self._ticker is not None:
            self._fetch_data()

        # Verify a good status code was received from the previous HTML
        # fetch before processing the HTML data
        if self.status_code == 200:
            self._process_data()

    def _process_data(self):
        """
        This method uses BeautifulSoup to parse through the HTML to find
        specific values of interest and returns a dictionary with keys specified
        by the strings used on the website. Dictionary values are themselves
        dictionaries with year as the key.
        """
        data = BeautifulSoup(self._response, "html.parser").find("table")

        if bool(data):
            # Need to pull out date info first before iterating through other
            # data. Date info has a row class that contains the string "date".
            # Select the first entry that has a class name that contains "date"
            # and parse out the <td> values, remove whitespaces, and match to
            # mm-YYYY format.
            self._get_dates(data, "tr[class*='date']", "td", "%m-%Y")

            # All stock data are contained within <tr> tags. Currently, only
            # stock are in <tr> tags. Use BeautifulSoup to return only data in
            # <tr> tags.
            trs = data.find_all("tr")

            # Loop through all found <tr> tags. If none are found, this block of
            # code is skipped and a warning message is added to the log as a
            # result.
            for row in trs:
                # Extract all values in <tr> row and remove all leading and
                # trailing whitespaces
                values_list = list(filter(None, map(lambda x: x.text.strip(),
                                                    row.find_all("td"))))

                # Replace bad characters. First index is field name so only
                # replace bad characters in all other indices.
                to_replace = {"$": "", ",": ""}
                values_list[1:] = list(
                    map(lambda x: self._multiple_replace(x, to_replace),
                        values_list[1:]))

                # Verify current <tr> is not a date row or summary row. Date
                # rows will contain the string "date" and summary rows only have
                # a length of one value.
                if "date" not in str(row) and len(values_list) > 1:

                    # Barchart presents data in 1000's. If not an EPS value,
                    # multiple values by 1000 and convert to integers. Convert
                    # EPS rows to floats.
                    if "EPS " in values_list[0]:
                        new_type = float
                        multiplier = 1
                    else:
                        new_type = int
                        multiplier = 1000

                    values_list[1:] = list(
                        map(lambda x: self._make_num(x, new_type) * multiplier,
                            values_list[1:]))

                    # Initialize data dictionary for the new field name. Then
                    # iterate through the data and update the dictionary with
                    # new {year: value} pairs.
                    if len(self._dates) == len(values_list[1:]):
                        self._data[values_list[0]] = {}
                        for ii in range(len(self._dates)):
                            self._data[values_list[0]].update(
                                {self._dates[ii]: values_list[ii + 1]})

                    else:
                        logger.error("Length of dates does not match length of "
                                     "data values for {} at {}. Got {} dates "
                                     "and {} values."
                                     "".format(self._ticker, self._url,
                                               len(self._dates),
                                               len(values_list[1:])))


class ScrapeTDAmeritradeHTML(FetchHTMLwithJavascript, StockScrapper):
    """Scrapes HTML data from TDAmeritrade.com.
    This class scrapes the HTML data on from TDAmeritrade.com to get values
    required to calculate the Big Five numbers from Rule 1. Currently
    TDAmeritrade is only used to calculate ROIC. The balance sheet is used to
    get Total Long Term Debt and Total Equity and the income statement is used
    to get the Net Income.

    TDAmeritrade uses javascript to render the page and also requires sessions.
    Use Selenium and Chrome to render the page content using the ticker symbol
    and then navigate to secondary links using the browser session to get to the
    desired data.

    Note
    ----
        Currently this is only used to get the shares outstanding needed to
        calculate book value per share.

    Parameters
    ----------
        :param: ticker : str
            Ticker symbol of a stock

    Attributes
    ----------

    Examples
    --------
        ScrapeTDAmeritradeHTML("AAPL")
        data = ScrapeTDAmeritradeHTML("AAPL").data

        Interface Definition:
            data[param_name][year] = value
    """

    def __init__(self, ticker: str):
        StockScrapper.__init__(self, ticker)
        # self._url = (r"https://research.tdameritrade.com/grid/public/"
        #              "research/stocks/fundamentals?symbol={}"
        #              "".format(self._ticker))
        # FetchHTML.__init__(self, "")

        # Ensure ticker is valid string
        if self._ticker is not None:
            # First url is landing point for fundamentals for the specified
            # ticker
            self._url = (r"https://research.tdameritrade.com/grid/public/"
                         "research/stocks/fundamentals?symbol={}"
                         "".format(self._ticker))

            FetchHTMLwithJavascript.__init__(self, self._url)
        else:
            self._status_code = 404
            return

        if self._url is not None:
            self._fetch_data()

        if self.status_code == 200:
            # Second url is the link embedded in the HTML returned from the
            # previous url. Following this link yields the balance sheet annual
            # data.
            self._url_next = ("https://research.tdameritrade.com/grid/public/"
                              "research/stocks/fundamentals/statement/"
                              "incomestatement?period=A")
            self._process_data()

            # To get balance sheet next, ensure the previous scrape returned
            # a good status code, then update the url_next attribute and re-run
            # the process_data method.
            self._url_next = (r"https://research.tdameritrade.com/grid/public/"
                              "research/stocks/fundamentals/statement/"
                              "balancesheet?period=A")

            self._process_data()
        else:
            pass

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

        self._response = self._driver.page_source

        data = BeautifulSoup(self._response, "html.parser")

        if bool(data):

            # Need to pull out date info first before iterating through other
            # data. Date info has a row class that contains the string
            # "period-header". Select the first entry that has a class name that
            # contains "period-header". When parsing out the <th> values, the
            # <br> tags collapse into a single date string with the format
            # YYYYmm/dd/yy.
            self._get_dates(data, "thead[class*='period-header']", "th",
                            "%Y%m/%d/%y")

            tables = data.find_all("table", {"class": ["section-content"]})
            for table in tables:

                # All stock data are contained within <tr> tags. Field names are
                # wrapped in <th> tags and values are wrapped in <td> tags.
                trs = table.find_all("tr")

                # Loop through all found <tr> tags. If none are found, this
                # block of code is skipped and a warning message is added to the
                # log as a result.
                for row in trs:

                    field = row.find("th").text
                    if field is not "":

                        # Extract all values in <tr> row and remove all leading
                        # and trailing whitespaces
                        values_list = list(
                            filter(None, map(lambda x: x.text.strip(),
                                             row.find_all("td"))))

                        # Replace bad characters.
                        to_replace = {"$": "", ",": "", "(": "-", ")": ""}
                        values_list = list(
                            map(lambda x: self._multiple_replace(x, to_replace),
                                values_list))

                        # TDAmeritrade presents data in millions. If not an EPS,
                        # value multiple values by 1000 and convert to integers.
                        # Convert EPS rows to floats.
                        if " EPS" in field:
                            new_type = float
                            multiplier = 1
                        else:
                            new_type = int
                            multiplier = 1000000

                        values_list = list(
                            map(lambda x: self._make_num(
                                x, new_type) * multiplier, values_list))

                        # Initialize data dictionary for the new field name.
                        # Then iterate through the data and update the
                        # dictionary with new {year: value} pairs.
                        if len(self._dates) == len(values_list):
                            self._data[field] = {}
                            for ii in range(len(self._dates)):
                                self._data[field].update(
                                    {self._dates[ii]: values_list[ii]})

                        else:
                            logger.error(
                                "Length of dates does not match length of data"
                                "values for {} at {}. Got {} dates and {} "
                                "values.".format(self._ticker, self._url,
                                                 len(self._dates),
                                                 len(values_list)))


class ScrapeMorningStarHTML(FetchHTMLwithJavascript, StockScrapper):
    """Scrapes HTML data from MorningStar.com.
    This class scrapes the HTML data on from MorningStar.com to get values
    required to calculate the Big Five numbers from Rule 1.

    Note
    ----


    Parameters
    ----------
        :param: ticker : str
            Ticker symbol of a stock

    Attributes
    ----------

    Examples
    --------
        ScrapeMorningStarHTML("AAPL")
        data = ScrapeMorningStarHTML("AAPL").data

        Interface Definition:
            data[param_name][year] = value
    """

    def __init__(self, ticker: str, statements: (list, str)=""):
        StockScrapper.__init__(self, ticker, statements)
        self._url = r"https://www.google.com/"
        # FetchHTML.__init__(self, "")

        # Ensure ticker is valid string
        if self._ticker is not None:
            # First url is landing point for fundamentals for the specified
            # ticker
            FetchHTMLwithJavascript.__init__(self, self._url)

            self._cur_dir = os.path.dirname(os.getcwd())
            # Set options in Chrome driver to enable downloads in Selenium
            self._driver.command_executor._commands["send_command"] = (
                "POST", '/session/$sessionId/chromium/send_command')

            params = {'cmd': 'Page.setDownloadBehavior',
                      'params': {'behavior': 'allow',
                                 'downloadPath': self._cur_dir}}
            self._driver.execute("send_command", params)

        else:
            self._status_code = 404
            return

        if self._url is not None:
            self._fetch_data()

        if self.status_code == 200:

            if "income" in statements:
                self._url = (r"http://financials.morningstar.com/"
                             "income-statement/is.html?t={}"
                             "".format(self._ticker))

                self._process_data()

            if "balance" in statements:
                self._url = (r"http://financials.morningstar.com/"
                             "balance-sheet/bs.html?t={}"
                             "".format(self._ticker))

                self._process_data()

            if "cash" in statements:
                self._url = (r"http://financials.morningstar.com/"
                             "cash-flow/cf.html?t={}"
                             "".format(self._ticker))

                self._process_data()

    def _process_data(self):
        self._driver.get(self._url)

        self._response = self._driver.page_source

        try:
            self._driver.find_element_by_css_selector(
                "a[class='rf_export']").click()

            # Get the most recent file added
            while True:
                try:
                    list_of_files = glob.glob(
                        self._cur_dir + r'\{} *.csv'.format(self._ticker))
                    latest_file = max(list_of_files, key=os.path.getctime)
                    break
                except ValueError:
                    time.sleep(0.05)

            with open(latest_file) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                next(csv_reader)  # Skip header row
                dates = next(csv_file).split(",")

                self._dates = list(map(
                    lambda x: datetime.datetime.strptime(
                        x.strip(), "%Y-%m").year, dates[1:-1]))

                for idx, row in enumerate(csv_reader):
                    pass

                    field = row[0]

                    # Replace bad characters
                    to_replace = {"$": "", ",": "", "(": "-", ")": ""}
                    values_list = list(
                        map(lambda x: self._multiple_replace(x, to_replace),
                            row[1:-1]))

                    if "diluted" in field.lower() or "basic" in field.lower():
                        # MorningStar does not have "EPS" in the field name. Need
                        # to check to see if there is a period in the value data to
                        # determine if values are basic/diluted EPS or average
                        # shares outstanding.
                        if "." in values_list[0]:
                            field += " EPS"
                            new_type = float
                            multiplier = 1
                        else:
                            field += " average shares outstanding"
                            new_type = int
                            multiplier = 1000000
                    else:
                        new_type = int
                        multiplier = 1000000

                    values_list = list(
                        map(lambda x: self._make_num(
                            x, new_type) * multiplier, values_list))

                    # Initialize data dictionary for the new field name.
                    # Then iterate through the data and update the
                    # dictionary with new {year: value} pairs.
                    if len(self._dates) == len(values_list):
                        self._data[field] = {}
                        for ii in range(len(self._dates)):
                            self._data[field].update(
                                {self._dates[ii]: values_list[ii]})

                    else:
                        logger.warning(
                            "Length of dates does not match length of data"
                            "values for {} at {}. Got {} dates and {} "
                            "values.".format(self._ticker, self._url,
                                             len(self._dates),
                                             len(values_list)))

            csv_file.close()
            os.remove(latest_file)
        except selenium.common.exceptions.NoSuchElementException:
            logger.warning("Data from {} could not be downloaded for {}"
                           "".format(self._url, self._ticker))


class ScrapeIEXTradingFinancialsJSON(FetchHTML, StockScrapper):
    """Implements IEXTrading API to retrieve JSON data.

    This class scrapes the JSON from API provided by IEXTrading.com to
    get values required to calculate shareholder equity Big Five number
    from Rule 1.

    Note
    ---
        Currently this is only used to get the shareholder equity.

    Parameters
    ----------
        :param: ticker : str
            Ticker symbol of a stock

    Attributes
    ----------

    Examples
    --------

        Usage: ScrapeIEXTradingFinancialsJSON("AAPL")
        data = ScrapeIEXTradingFinancialsJSON("AAPL").data

        Interface Definition:
            data[param_name][year] = value
    """

    def __init__(self, ticker: str):
        StockScrapper.__init__(self, ticker)
        FetchHTML.__init__(self, "https://api.iextrading.com/1.0/stock/{}/"
                                 "financials?period=annual"
                                 "".format(self._ticker))

        # Check to ensure the _ticker and _url are defined. If both exist, fetch
        # HTML code
        if self._ticker is not None and self._url is not None:
            self._fetch_data()

        # Verify a good status code was received before processing the HTML data
        if self.status_code == 200:
            self._process_data()

    def _process_data(self):
        """Strip HTML tags from JSON response

        All data are under the "financial" key at the top level JSON structure.
        The resulting value is a list of dicts. Each year of data are stored as
        an dictionary as an entry in the list. The structure of the yearly data
        is {param_name : value}. The data structure is as follows:

        "financials": [{param1: value1, param2: value2, ...}, {...}, ...}]

        Parameters
        ----------

        Returns
        -------

        """

        try:
            data = json.loads(re.sub('<[^<]+?>', '', self._response))

            # Iterate through list values for different years of data
            tmp_date = None
            for ii in data["financials"]:

                # Get date information first. IEXTrading uses YYYY-mm-dd format
                tmp_date = datetime.datetime.strptime(ii["reportDate"],
                                                      "%Y-%m-%d")
                tmp_year = tmp_date.year

                # Iterate through data for the given year where key is the
                # parameter name and value is the corresponding parameter value.
                for key, value in ii.items():
                    if not key == "reportDate":
                        # Attempt to add new value to _data. The first time
                        # "key" is used, a KeyError is raised so initialize
                        # _data with the key and {year : value} dictionary.
                        try:
                            # If the value is not a number (e.g., "--", or
                            # "null"), return a numpy.NaN value.
                            if value is None:
                                value = np.NaN
                            self._data[key][tmp_year] = float(value)
                        except KeyError:
                            self._data[key] = {tmp_year: float(value)}
                        except TypeError:
                            self._data[key] = {tmp_year: np.NaN}
                            logger.error("TypeError occurred with ticker {} on "
                                         "IEXTrading.com for key {}"
                                         "".format(self._ticker, key))
                        except ValueError:
                            self._data[key] = {tmp_year: np.NaN}
                            self._log_bad_value(self._url, value, key)

                # When a new year is encountered, append it to _dates
                self._dates.append(tmp_year)

            self._report_month = tmp_date.month

        except KeyError:
            logger.error("Failed to read JSON data for ticker {} from "
                         "IEXTrade.com".format(self._ticker))

        except json.JSONDecodeError:
            logger.error("Failed to read JSON data for ticker {} from "
                         "IEXTrade.com".format(self._ticker))


class ScrapeFinancialModelingPrepJSON(FetchHTML, StockScrapper):
    """Implements FinancialModelingPrep API to retrieve JSON data.

    This class scrapes the JSON from API provided by FinancialModelingPrep.com
    to get values required to calculate Sales, EPS, and Cash Flow Big Five
    numbers from Rule 1.

    Note
    ----
        Currently this is only used to get the shareholder equity.

    Parameters
    ----------
        :param: ticker : str
            Ticker symbol of a stock

    Attributes
    ----------

    Examples
    --------

        Usage: ScrapeFinancialModelingPrepJSON("AAPL")
        data = ScrapeFinancialModelingPrepJSON("AAPL").data

        Interface Definition:
            data[param_name][year] = value
    """

    def __init__(self, ticker: str):
        StockScrapper.__init__(self, ticker)
        FetchHTML.__init__(self, "https://financialmodelingprep.com/api/"
                                 "financials/income-statement/{}"
                                 "".format(self._ticker))

        # The version of the API to implement when retrieving data. Currently
        # FinancialModelingPrep only has v1.0.
        self._fmp_version = "1.0"

        # Check to ensure the _ticker and _url are defined. If both exist, fetch
        # HTML code
        if self._ticker is not None and self._url is not None:
            self._fetch_data()

        # Verify a good status code was received before processing the HTML data
        if self.status_code == 200:
            self._process_data()

        # Define second url to retrieve JSON data from. Data from this url will
        # be appended to _data
        self._url = ("https://financialmodelingprep.com/api/financials/"
                     "balance-sheet-statement/{}".format(self._ticker))

        if self._ticker is not None:
            self._fetch_data()

        # Verify a good status code was received from the previous HTML fetch
        # before processing the HTML data
        if self.status_code == 200:
            self._process_data()

    def _api_v1_0(self, data):
        """Use version 1.0 of the API to process the JSON data

        Parameters
        ----------
            :param data: JSON data that has been stripped of HTML tags

        Returns
        -------

        """

        # The primary key at the top level JSON structure is the stock
        # ticker
        tmp_date = None
        tmp_year = None

        try:
            # Verify that the fetched JSON data set is not empty before
            # processing the data.
            # In v1.0, FinancialModelingPrep structures the data with nested
            # dictionaries with the following format:
            # {ticker : {param_name: {value1, value2, ...}, ...} }
            if bool(data[self._ticker].values()):

                # Iterates through the first set of dict keys which are the
                # parameter names as strings.
                for field, year_value in data[self._ticker].items():

                    # Iterate through the nested dictionary which is year:value
                    # sets
                    for year, value in year_value.items():
                        try:
                            # This version of the API provides dates in YYYY-mm
                            # format
                            tmp_date = datetime.datetime.strptime(
                                year, "%Y-%m")
                            tmp_year = tmp_date.year

                            # Attempt to add new value to _data. The first time
                            # "key" is used, a KeyError is raised so initialize
                            # _data with the key and {year : value} dictionary.
                            try:

                                # Data are provided in millions. Attempt to
                                # convert value to float and multiply by 1e6.
                                try:
                                    value = float(value) * 1e6

                                # If the value is not a number (e.g., "--", or
                                # "null"), return a numpy.NaN value.
                                except ValueError:
                                    value = np.NaN
                                    self._log_bad_value(self._url, value, field)

                                self._data[field][tmp_year] = value

                            except KeyError:
                                self._data[field] = {tmp_year: value}
                        except ValueError:
                            pass

                        # When a new year is encountered, append it to _dates
                        if tmp_year not in self._dates:
                            self._dates.append(tmp_year)
                    self._report_month = tmp_date.month

            else:
                # If data already exists in _data from a previous iteration, do
                # not a bad set status code.
                if not bool(self._data):
                    self._status_code = 404

        except KeyError:
            logger.error("Failed to read JSON data for ticker {} from "
                         "IEXTrade.com".format(self._ticker))

        except json.JSONDecodeError:
            logger.error("Failed to read JSON data for ticker {} from "
                         "IEXTrade.com".format(self._ticker))

    def _process_data(self):
            # Strip HTML tags from JSON response
            data = json.loads(re.sub('<[^<]+?>', '',
                                     requests.get(self._url).text))

            # Check the API version and call the correct api processor
            if self._fmp_version == "1.0":
                self._api_v1_0(data)

            # Catch all other API versions as errors
            else:
                logger.error("Unknown API version {} was provided for {}. "
                             "Current valid API(s) are [1.0, ]."
                             "".format(self._fmp_version, self._url))

    pass


class CalcBigFive(ABC):
    """Abstract class for calculating Rule1 Big Five numbers.

    This class provides the basic structure required for calculating the Big
    Five numbers. Specifically, this class provides the methods to initialize
    any or all of the defined Scraping functions as needed by the user.

    No public attributes are defined for this class.

    Parameters
    ----------
        :param str ticker: Ticker of the stock

        :param int year: Year for which data is desired

        :param int redundancy: Number of calculations to perform and compare.
            Use for additional confidence in response.

    Attributes
    ----------
    """
    def __init__(self, ticker: str, year: int=-1, redundancy: int=1):

        # Public Variables
        self._ticker = ticker
        self._year = year
        self._err_code = None
        self._redundancy = redundancy
        self._confidence = [68, 95, 99.7]

        # Private Data Containers from Scraping
        self._bar = None  # Barchart.com
        self._tda = None  # TDAmeritrade.com (webdriver = very slow!)
        self._iex = None  # IEXTrading JSON API
        self._fmp = None  # FinancialModelingPrep JSON API

        # Verify that the provided year is of type int.
        try:
            assert isinstance(year, int)
        except AssertionError:
            self._err_code = 1  # Bad year type
            logger.error("Expect type int for year, got {} for ticker {}"
                         "".format(type(self._ticker), self._ticker))

    def __repr__(self):
        return self._err_code

    def _barchart(self):
        """Get data from Barchart.com"""
        if not bool(self._bar):
            # self._bar = None
            # tmp = ScrapeBarchartHTML(self._ticker)
            # if tmp.status_code == 200:
            #     self._bar = tmp
            self._bar = ScrapeBarchartHTML(self._ticker)

    def _tdameritrade(self):
        """Get data from TDAmeritrade.com"""
        if not bool(self._tda):
            self._tda = ScrapeTDAmeritradeHTML(self._ticker)

    def _iextrading(self):
        """Get data from IEXTrading API"""
        if not bool(self._iex):
            self._iex = ScrapeIEXTradingFinancialsJSON(self._ticker)

    def _financial_modeling_prep(self):
        """Get data from FinancialModelingPrep API"""
        if not bool(self._fmp):
            self._fmp = ScrapeFinancialModelingPrepJSON(self._ticker)

    @abstractmethod
    def _calc_method1(self):
        pass

    @abstractmethod
    def _calc_method2(self):
        pass

    @abstractmethod
    def _calc_method3(self):
        pass

    def _value_by_year(self, tmp_dict, big_five, source):
        if bool(tmp_dict):
            if self._year == -1:
                self._year = np.max(np.array(list(tmp_dict.keys())))

            if self._year in np.array(list(tmp_dict.keys())):
                return tmp_dict[self._year]
            else:
                self._bad_year()
                return None

        else:
            self._log_calc_err(big_five, source)
            return None

    def _bad_year(self):
        this_year = datetime.datetime.now().year
        if this_year - 1 < self._year == this_year:
            self._err_code = 2
            logger.error("Error calculating EPS for {}. Specified year {y} "
                         "not found in financial data. Has data for {y} "
                         "been released?"
                         "".format(self._ticker, y=self._year))

        elif self._year > this_year:
            self._err_code = 2
            logger.error("Error calculating EPS for {}. Specified year {} "
                         "is in the future."
                         "".format(self._ticker, self._year))

        elif self._year < this_year - 3:
            self._err_code = 3
            logger.error("Error calculating EPS for {}. Specified year {} "
                         "is more than three years in the past. Not all "
                         "data sources provide more than three years of "
                         "historical data."
                         "".format(self._ticker, self._year))

    def _log_calc_err(self, big_five, source):
        logger.error("Failed to calculate {} data for {} from ".format(
            big_five, self._ticker, source))

    @property
    def ticker(self):
        return self._ticker

    @property
    def err_code(self):
        return self._err_code

    @property
    def confidence(self):
        return self._confidence


class CalcEPS(CalcBigFive):
    """Calculates the EPS for the given stock ticker.

    Uses Scraping classes to find the necessary data elements to calculate the
    diluted EPS for the given stock ticker.

    Primary preference is to use faster JSON APIs and calculate the EPS using a
    standard formula. Secondary preferences is to use HTML scraping to get EPS
    directly or, failing that, scrape missing variables required to calculate
    the EPS.

    Parameters
    ----------
        :param: ticker : str
            Ticker symbol of a stock

        :param: year : int
            Year for which eps data is desired

    Examples
    --------
        CalcEPS("AAPL")
        eps = CalcEPS("AAPL").eps
        eps = CalcEPS("AAPL", 2017).eps
    """
    def __init__(self, ticker: str, year: int=-1, redundancy: int=2):
        CalcBigFive.__init__(self, ticker, year, redundancy)

        # Public Variables
        self._eps = None

        # Private Variables
        self._net_income_comm = None
        self._diluted_shares = None

        # Get data and calculate eps
        # self._get_net_income()
        # self._get_diluted_shares()
        self._calc_eps()

    def _calc_method1(self) -> int:
        """Use FinancialModelingPrep API to calculate EPS.

        Use net income available to common shareholders and diluted shares to
        calculate EPS.

        Equation Used:
            I_com = Net Income Available to Common Shareholders
            S_dil = Diluted Shares
            EPS = I_com / S_dil

        Parameters
        ----------

        Returns
        -------
            :return float: EPS value corresponding to the provided year
        """
        self._financial_modeling_prep()
        if self._fmp.status_code == 200:
            try:

                income = self._fmp.data[
                    "Net income available to common shareholders"]
                shares = self._fmp.data["Diluted"]

                tmp_eps = {k: income[k] / shares[k] for k
                           in shares.keys() & income}

                return self._value_by_year(tmp_eps, "EPS",
                                           "FinancialModelingPrep API")
            except KeyError as e:
                logger.error("Failed to find field for {}. {}".format(
                    self._ticker, e))

    def _calc_method2(self) -> int:
        """Get EPS from Barchart.com.

        Uses income statement data from Barchart.com to get the diluted EPS.

        Parameters
        ----------

        Returns
        -------
            :return float: EPS value corresponding to the provided year
        """
        self._barchart()
        if self._bar.status_code == 200:
            try:

                return self._value_by_year(self._bar.data[
                                           "EPS Diluted Total Ops"],
                                           "EPS", "FinancialModelingPrep API")
            except KeyError as e:
                logger.error("Failed to find field for {}. {}".format(
                    self._ticker, e))

    def _calc_method3(self) -> int:
        """Get EPS from TDAmeritrade.com.

        Uses income sheet data from Barchart.com to get the diluted EPS.

        Parameters
        ----------

        Returns
        -------
            :return float: EPS value corresponding to the provided year
        """
        pass  # lots of errors on TDAmeritrade
        # self._tdameritrade()
        # if self._tda.status_code == 200:
        #     try:
        #         return self._value_by_year(
        #             self._tda.data["Diluted Normalized EPS"],
        #             "EPS", "FinancialModelingPrep API")
        #
        #     except KeyError as e:
        #         logger.error("Failed to find field for {}. {}".format(
        #             self._ticker, e))

    def _calc_eps(self):

        # TODO - Consider replacing with map passing the calc methods
        tmp_list_redundant = list()
        tmp_eps = self._calc_method1()
        if tmp_eps is not None and len(tmp_list_redundant) < self._redundancy:
            tmp_list_redundant.append(tmp_eps)

        if len(tmp_list_redundant) < self._redundancy:
            tmp_eps = self._calc_method2()
            if tmp_eps is not None:
                tmp_list_redundant.append(tmp_eps)

        if len(tmp_list_redundant) < self._redundancy:
            tmp_eps = self._calc_method3()
            if tmp_eps is not None:
                tmp_list_redundant.append(tmp_eps)

        if bool(tmp_list_redundant):
            delta_list = list()
            for ii in range(len(tmp_list_redundant) - 1):
                delta_list.append(np.isclose(tmp_list_redundant[ii + 1],
                                             tmp_list_redundant[ii], atol=1e-1))

            are_true = np.where(delta_list)[0]

            try:
                self._eps = tmp_list_redundant[are_true[0]]
                self._confidence = self._confidence[len(are_true)]

            # If all values are different, go with the eps provided by the
            # highest priority method that was not None.
            except IndexError:
                self._eps = tmp_list_redundant[0]
                self._confidence = 0
        else:
            self._eps = None
            self._confidence = None

    @property
    def eps(self):
        return self._eps


class FetchTickers(FetchHTML):
    """Get stock name and tickers.

    Attributes
    ----------

    Parameters
    ----------

    """
    def __init__(self):

        # https://www.nasdaq.com/screening/company-list.aspx
        url_nasdaq = ("https://www.nasdaq.com/screening/companies-by-name.aspx"
                      "?letter=0&exchange=nasdaq&render=download")
        url_nyse = ("https://www.nasdaq.com/screening/companies-by-name.aspx"
                    "?letter=0&exchange=nyse&render=download")
        url_amex = ("https://www.nasdaq.com/screening/companies-by-name.aspx"
                    "?letter=0&exchange=amex&render=download")

        FetchHTML.__init__(self, url_nasdaq)

        self._data = list()

        # Check to ensure the _ticker and _url are defined. If both exist, fetch
        # HTML code
        if self._url is not None:
            self._fetch_data()
            self._process_data()

        self._url = url_nyse
        if self._url is not None:
            self._fetch_data()
            self._process_data()

        self._url = url_amex
        if self._url is not None:
            self._fetch_data()
            self._process_data()

    def _process_data(self):
        if "Symbol" and "Name" in self._response.splitlines()[0]:
            self._data += list(map(lambda x: x.replace('"', "").replace(
                "&#39;", "'").split(","), self._response.splitlines()[1:]))
        else:
            self._data += list(map(lambda x: x.replace('"', "").replace(
                "&#39;", "'").split(","), self._response.splitlines()))

    @property
    def data(self):
        """
        list: List of stock names and stock tickers for NASDAQ, NYSE, and AMEX
            exchanges with the format [[name1, ticker1], [name2, ticker2], ...]
        """
        tmp_list = list()
        for row in self._data:
            tmp_list.append([row[1].strip(), row[0].strip()])
        return tmp_list




# TODO: CalcEPS Class
# TODO: CalcCashFlow Class
# TODO: CalcBVPS Class
# TODO: CalcSales Class
# TODO: CalcROIC Class


logger = RuleOneLogger().logger

if __name__ == "__main__":
    pass
