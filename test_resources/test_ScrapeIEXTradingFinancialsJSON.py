from unittest import TestCase
import rule_one_utils


tester_ip = "192.168.1.12"


class TestScrapeIEXTradingFinancialsJSON(TestCase):
    def test__process_data_good_data(self):
        """Tests if a good ticker is provided to IEXTrading.com JSON API"""
        tester = rule_one_utils.ScrapeIEXTradingFinancialsJSON("AAPL")
        tester._url = ("http://{}/test_resources/iextrading_good.html"
                       "".format(tester_ip))
        tester._data = {}
        tester._fetch_data()
        tester._process_data()
        self.assertTrue(tester.status_code == 200 and bool(tester.data))

    def test__process_data_bad_ticker_type(self):
        """Tests if a bad ticker is provided to IEXTrading.com JSON API"""
        tester = rule_one_utils.ScrapeIEXTradingFinancialsJSON(123)
        self.assertEqual(tester.status_code, 404)

    def test__process_data_bad_ticker(self):
        """Tests if a bad ticker is provided to IEXTrading.com JSON API"""
        tester = rule_one_utils.ScrapeIEXTradingFinancialsJSON("123")
        self.assertEqual(tester.status_code, 404)

    def test__process_data_bad_value(self):
        """Test if the IEXTrading.com API handles bad data.
        File has '--' as bad values. JSON throws error if a non-numeric value is
        provided and the code returns an empty set.
        """
        tester = rule_one_utils.ScrapeIEXTradingFinancialsJSON("AAPL")
        tester._data = {}

        tester._url = ("http://{}/test_resources/iextrading_bad_values.html"
                       "".format(tester_ip))
        tester._fetch_data()
        self.assertTrue(not bool(tester.data))
