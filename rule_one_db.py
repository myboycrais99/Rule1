"""
This library provides the necessary classes and methods to provide an API to
access, update, and fetch data from the Rule1 database.
"""

import pymysql
from rule_one_utils import RuleOneLogger
logger = RuleOneLogger().logger


class RuleOneDatabase(object):
    """


    Parameters
    ----------
        :param str host: hostname or ip address where database server is located
        :param str user: user name
        :param str password: user password

        #TODO - remove password string and replace with protected file
    """

    def __init__(self, host, db, user, password):
        self._connect_db(host, db, user, password)
        logger.debug("User '{}' connected to database '{}' at host '{}'".format(
            user, db, host))

    def _connect_db(self, host: str, db: str, user: str, password: str):
        """Connect to the database.

        Parameters
        ----------
            :param str host: hostname or ip address where database server is
                located
            :param str db: name of the database
            :param str user: user name
            :param str password: user password

        Returns
        -------

        """
        self._conn = pymysql.connect(host=host,
                                     user=user,
                                     password=password,  # root; rule1-password
                                     db=db,
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

    def _disconnect_db(self):
        """Closes connection to database.

        Parameters
        ----------

        Returns
        -------

        """
        self._conn.close()

    def add_company(self, name: str, ticker: str, month: (None, int)):
        """Add new company to database.

        Parameters
        ----------
            :param str name: Name of the company. Must be <= 120 char
            :param str ticker: Company Ticker. Must be <= 10 char
            :param int month: Month that financial reports are available

        Returns
        -------

        """
        try:
            assert isinstance(name, str)
            assert len(name) <= 120
            assert isinstance(ticker, str)
            assert len(ticker) <= 10
            assert (isinstance(month, int) or month is None)
            assert (month in range(1, 13) or month is None)
        except AssertionError:
            logger.error("Bad parameters passed when adding company to Rule 1 "
                         "database for {}.".format(ticker), exc_info=True)
            return list()

        try:
            with self._conn.cursor() as cur:
                cur.callproc("addStock", [name, ticker, month])
                self._conn.commit()

            logger.debug("Successfully added {} to Rule1 database."
                         "".format(ticker))

        except self._conn.IntegrityError as e:
            logger.info("Insertion Error. Error code {}. {}".format(e.args[0],
                                                                    e.args[1]))

    def delete_company(self, ticker: str):
        """Deletes company from Rule1 database.

        This function deletes the company identified by "ticker" from the Rule1
        database. Delete is "CASCADE" so all Big5 numbers associated with the
        ticker are also deleted from the database. Consider updating the stock
        flag "IsActive" to 0 to preserve data but exclude stock from future
        searches and data processing.

        Parameters
        ----------
            :param str ticker: stock ticker

        Returns
        -------

        """
        try:
            assert isinstance(ticker, str)
            assert len(ticker) <= 10
        except AssertionError:
            logger.error("Bad parameters passed when deleting company from "
                         "Rule1 database for {}.".format(ticker), exc_info=True)
            return list()

        try:
            with self._conn.cursor() as cur:
                cur.callproc("deleteStock", [ticker])
                self._conn.commit()

            logger.debug("Successfully deleted {} from Rule1 database."
                         "".format(ticker))

        except self._conn.IntegrityError as e:
            logger.error("Deletion Error. Attempted to delete {} from "
                         "database. Got error {}".format(ticker, e.args[1]))

    def update_company(self, ticker: str, month: (None, int),
                       is_active: (None, int)=None,
                       has_financials: (None, int)=None):
        """Update stock to indicate if it is active and has financial data.

        This method enables the user to later update a stock that no longer
        exists rather than deleting the stock and removing historic data. Or if
        the stock no longer has financial data published this removes them from
        future web scraping and data processing.

        Parameters
        ----------
            :param str ticker: stock ticker
            :param int month: month when financial reports are release
            :param int is_active: Boolean integer that indicates if stock is
                still actively traded.
            :param int has_financials: Boolean integer that indicates if stock
                has financials published. For instance, some tickers are only
                indexes and have no financial statements published.

        Returns
        -------

        """
        try:
            assert isinstance(ticker, str)
            assert isinstance(month, int)
            assert is_active in [None, 0, 1]
            assert has_financials in [None, 0, 1]
        except AssertionError:
            logger.error("Bad parameters passed when deleting company from "
                         "Rule1 database for {}.".format(ticker), exc_info=True)
            return list()

        try:
            with self._conn.cursor() as cur:
                if month is not None:
                    cur.callproc("updateStockMonth",
                                 [ticker, month])

                    logger.debug("Successfully updated {} 'ReportMonth' to {}"
                                 "".format(ticker, month))
                    self._conn.commit()

                if is_active is not None:
                    cur.callproc("updateStockIsActive",
                                 [ticker, is_active])

                    logger.debug("Successfully updated {} 'IsActive' to {}"
                                 "".format(ticker, is_active))
                    self._conn.commit()

                if has_financials is not None:
                    cur.callproc("updateStockHasFinancials",
                                 [ticker, has_financials])

                    logger.debug("Successfully updated {} 'HasFinancials' to {}"
                                 "".format(ticker, has_financials))
                    self._conn.commit()

        except self._conn.IntegrityError as e:
            logger.error("Update Error. Attempted to update 'IsActive' and "
                         "'HasFinances' for {} in Rule1 database. Got error {}"
                         "".format(ticker, e.args[1]))

    def get_stocks(self, active: bool=True):
        """Get all stocks currently in Rule1 database.

        This method returns all of the stocks in th Rule1 database. User has the
        option of returning only actively traded stocks with financial data
        (default) or to return all stocks in database.

        Parameters
        ----------
            :param active: optional. If True, only return stocks that are
                actively traded and have financials for calculating Big5
                numbers. False returns all stocks in database.
        Returns
        -------
            :return list(dict): List of dictionaries containing rows from
                database query for all stocks currently in the database.
        """
        try:
            assert isinstance(active, bool)
        except AssertionError:
            logger.error("Bad parameters passed when getting stocks from "
                         "Rule1 database for {}.", exc_info=True)
            return list()

        with self._conn.cursor() as cur:
            if active:
                logger.debug("Returning active stocks in Rule1 database")
                cur.callproc("getActiveTickers")
            else:
                logger.debug("Returning all stocks in Rule1 database")
                cur.callproc("getStocks")

            return cur.fetchall()

    def get_big5(self, ticker: str, year: (None, int, list) = None) -> list:
        """Return the Big 5 numbers for a given ticker and year.

        Returns all the EPS, Cash Flow, BVPS, Sales, and ROIC data for a given
        ticker. Optionally, the user can specify a single year or start and end
        years to restrict the data returned to the desired year(s).

        Parameters
        ----------
            :param str ticker:
            :param int year:

        Returns
        -------
            :return list(dict): List of dictionaries containing rows from the
                database query. If an error occurs, the returned list is empty.
        """

        try:
            assert isinstance(ticker, str)
            assert isinstance(year, (int, list))
            if isinstance(year, list):
                assert len(year) == 2
                assert isinstance(year[0], int)
                assert isinstance(year[1], int)
        except AssertionError:
            logger.error("Bad parameters passed when getting Big5 data from "
                         "Rule1 database for {}.".format(ticker), exc_info=True)
            return list()

        with self._conn.cursor() as cur:

            # No year provided. Return all years.
            if year is None:
                logger.debug("Returning all Big5 numbers for {}".format(ticker))
                cur.callproc("getAllforTicker", [ticker])

            # Single year provided. Can be int or list.
            elif isinstance(year, int):
                cur.callproc("getAllforTickerYear", [ticker, year])

            # List of years provided. Provide data for all found within the
            # inclusive set of years.
            elif isinstance(year, list):
                cur.callproc("getAllforTickerYears", [ticker, year[0], year[1]])

            # Unknown amount of years provided.
            else:
                logger.warning("Failed to retrieve Big5 data for {} from Rule1 "
                               "database.".format(ticker))
                return list()

            logger.debug("Successfully retrieved Big5 data for {} from Rule1 "
                         "database.".format(ticker))
            return cur.fetchall()

    def add_eps(self, ticker: str, year: int, eps: (float, int)):
        """Add EPS data for a ticker and year pair do the Rule1 database.

        Creates a new entry in the EPS table for the stock defined by "ticker"
        for the year defined by "year". The combination of ticker and year must
        be unique or it will be rejected by the database.

        Parameters
        ----------
            :param str ticker: stock ticker
            :param int year: year for which the data is applicable
            :param float eps: earnings per share (eps) data for the stock

        Returns
        -------

        """
        try:
            assert isinstance(ticker, str)
            assert isinstance(year, int)
            assert isinstance(eps, (int, float))
        except AssertionError:
            logger.error("Bad parameters passed when adding EPS data to Rule 1 "
                         "database for {}.".format(ticker), exc_info=True)

        try:
            with self._conn.cursor() as cur:
                cur.callproc("addEPS", [ticker, year, eps])
                self._conn.commit()

            logger.debug("Successfully added {} EPS data for {} to Rule1 "
                         "database.".format(year, ticker))

        except self._conn.IntegrityError as e:
            logger.error("Insertion Error. Attempted to add EPS data for {} "
                         "into the Rule1 database. Got error {}"
                         "".format(ticker, e.args[1]))

    def add_cash_flow(self, ticker: str, year: int, cash_flow: int):
        """Add Cash Flow data for a ticker and year pair do the Rule1 database.

        Creates a new entry in the cash_flow table for the stock defined by
        "ticker" for the year defined by "year". The combination of ticker and
        year must be unique or it will be rejected by the database.

        Parameters
        ----------
            :param str ticker: stock ticker
            :param int year: year for which the data is applicable
            :param float cash_flow: cash flow data for the stock

        Returns
        -------

        """
        try:
            assert isinstance(ticker, str)
            assert isinstance(year, int)
            assert isinstance(cash_flow, int)
        except AssertionError:
            logger.error("Bad parameters passed when adding Cash Flow data to "
                         "Rule 1 database for {}."
                         "".format(ticker), exc_info=True)

        try:
            with self._conn.cursor() as cur:
                cur.callproc("addCashFlow", [ticker, year, cash_flow])
                self._conn.commit()

            logger.debug("Successfully added {} Cash Flow data for {} to Rule1 "
                         "database.".format(year, ticker))

        except self._conn.IntegrityError as e:
            logger.error("Insertion Error. Attempted to add Cash Flow data for "
                         "{} into the Rule1 database. Got error {}"
                         "".format(ticker, e.args[1]))

    def add_bvps(self, ticker: str, year: int, bvps: (float, int)):
        """Add BVPS data for a ticker and year pair do the Rule1 database.

        Creates a new entry in the BVPS table for the stock defined by "ticker"
        for the year defined by "year". The combination of ticker and year must
        be unique or it will be rejected by the database.

        Parameters
        ----------
            :param str ticker: stock ticker
            :param int year: year for which the data is applicable
            :param float bvps: book value per share (bvps) data for the stock

        Returns
        -------

        """
        try:
            assert isinstance(ticker, str)
            assert isinstance(year, int)
            assert isinstance(bvps, (int, float))
        except AssertionError:
            logger.error("Bad parameters passed when adding BVPS data to Rule "
                         "1 database for {}.".format(ticker), exc_info=True)

        try:
            with self._conn.cursor() as cur:
                cur.callproc("addBVPS", [ticker, year, bvps])
                self._conn.commit()

            logger.debug("Successfully added {} BVPS data for {} to Rule1 "
                         "database.".format(year, ticker))

        except self._conn.IntegrityError as e:
            logger.error("Insertion Error. Attempted to add BVPS data for {} "
                         "into the Rule1 database. Got error {}"
                         "".format(ticker, e.args[1]))

    def add_sales(self, ticker: str, year: int, sales: int):
        """Add Sales data for a ticker and year pair do the Rule1 database.

        Creates a new entry in the Sales table for the stock defined by "ticker"
        for the year defined by "year". The combination of ticker and year must
        be unique or it will be rejected by the database.

        Parameters
        ----------
            :param str ticker: stock ticker
            :param int year: year for which the data is applicable
            :param float sales: sales data for the stock

        Returns
        -------

        """
        try:
            assert isinstance(ticker, str)
            assert isinstance(year, int)
            assert isinstance(sales, int)
        except AssertionError:
            logger.error("Bad parameters passed when adding Sales data to Rule "
                         "1 database for {}.".format(ticker), exc_info=True)

        try:
            with self._conn.cursor() as cur:
                cur.callproc("addSales", [ticker, year, sales])
                self._conn.commit()

            logger.debug("Successfully added {} sales data for {} to Rule1 "
                         "database.".format(year, ticker))

        except self._conn.IntegrityError as e:
            logger.error("Insertion Error. Attempted to add sales data for {} "
                         "into the Rule1 database. Got error {}"
                         "".format(ticker, e.args[1]))

    def add_roic(self, ticker: str, year: int, roic: (float, int)):
        """Add EPS data for a ticker and year pair do the Rule1 database.

        Creates a new entry in the EPS table for the stock defined by "ticker"
        for the year defined by "year". The combination of ticker and year must
        be unique or it will be rejected by the database.

        Parameters
        ----------
            :param str ticker: stock ticker
            :param int year: year for which the data is applicable
            :param float roic: return on investment capital (roic) for the stock

        Returns
        -------

        """
        try:
            assert isinstance(ticker, str)
            assert isinstance(year, int)
            assert isinstance(roic, (int, float))
        except AssertionError:
            logger.error("Bad parameters passed when adding ROIC data to Rule "
                         "1 database for {}.".format(ticker), exc_info=True)

        try:
            with self._conn.cursor() as cur:
                cur.callproc("addROIC", [ticker, year, roic])
                self._conn.commit()

            logger.debug("Successfully added {} ROIC data for {} to Rule1 "
                         "database.".format(year, ticker))

        except self._conn.IntegrityError as e:
            logger.error("Insertion Error. Attempted to add ROIC data for {} "
                         "into the Rule1 database. Got error {}"
                         "".format(ticker, e.args[1]))


if __name__ == "__main__":
    bob = RuleOneDatabase(host='localhost', db='rule1_devdb', user='ryan',
                          password='password')  # rule1-password

    # bob.delete_company("CEM")
    # bob.add_company("CLEARBRIDGE ENERGY MLP", "CEM", None)
    # bob.update_company("CEM", is_active=0, has_financials=0)
    # bob.add_eps("CEM", year=2017, eps=1.0)
    # # print(bob.get_big5("AAPL", 2017))
    # print(bob.get_stocks())

