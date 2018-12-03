from unittest import TestCase
import rule_one_utils
from selenium import webdriver


tester_ip = "192.168.1.12"


class TestScrapeTDAmeritradeHTML(TestCase):

    def test__process_good_data(self):
        """Tests if a good ticker is provided to TDAmeritrade.com"""
        tester = rule_one_utils.ScrapeTDAmeritradeHTML("AAPL")

        options = webdriver.ChromeOptions()
        options.headless = True
        tester._driver = webdriver.Chrome(options=options)

        tester._data = {}
        tester._url = (r"http://{}/test_resources/tdameritrade_fundamentals"
                       "_good.html".format(tester_ip))

        tester._url_next = (r"http://{}/test_resources/tdameritrade_balance_"
                            "sheet_good.html".format(tester_ip))
        tester._fetch_data()
        tester._process_data()
        tester._driver.quit()
        self.assertTrue(tester.status_code == 200 and "?symbol={}"
                        "".format(tester._ticker) in tester._response)

    def test__process_data_bad_ticker_type(self):
        """Test if TDAmeritrade.com scraper handles wrong ticker type"""
        tester = rule_one_utils.ScrapeTDAmeritradeHTML(123)
        self.assertEqual(tester.status_code, 404)

    def test__process_data_bad_ticker(self):
        """Test if TDAmeritrade.com scraper handles a bad ticker"""
        tester = rule_one_utils.ScrapeTDAmeritradeHTML("123")
        self.assertEqual(tester.status_code, 404)

    def test__process_data_bad_value(self):
        """Test if TDAmeritrade.com scraper handles bad data.
        File has 'NaN', 'Ryan' and '++' as bad values. Code lets 'NaN' through
        but converts the others to np.NaNs."""
        try:
            tester = rule_one_utils.ScrapeTDAmeritradeHTML("AAPL")

            options = webdriver.ChromeOptions()
            options.headless = True
            tester._driver = webdriver.Chrome(options=options)

            tester._data = {}
            tester._url = (r"http://{}/test_resources/tdameritrade_fundamentals"
                           "_good.html".format(tester_ip))

            tester._url_next = (r"http://{}/test_resources/tdameritrade_balance"
                                "_sheet_bad_values.html".format(tester_ip))
            tester._fetch_data()
            tester._driver.quit()
            self.assertTrue(tester.status_code == 200 and
                            "?symbol={}".format(tester._ticker) in
                            tester._response)

        except ValueError as e:
            self.fail("Failed with error '{}'".format(e))
