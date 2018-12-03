from unittest import TestCase
import rule_one_utils


tester_ip = "192.168.1.12"


class TestScrapeFinancialModelingPrepJSON(TestCase):
    def test__process_data_good_data(self):
        """Tests if good ticker is provided to FinancialModelingPrep API"""
        tester = rule_one_utils.ScrapeFinancialModelingPrepJSON("AAPL")
        tester._url = ("http://{}/test_resources/financialmodelingprep_good"
                       ".html".format(tester_ip))
        tester._data = {}
        tester._fetch_data()
        tester._process_data()
        self.assertTrue(tester.status_code == 200 and bool(tester.data))

    def test__process_data_bad_ticker_type(self):
        """Tests if bad ticker type is provided to FinancialModelingPrep API"""
        tester = rule_one_utils.ScrapeFinancialModelingPrepJSON(123)
        self.assertEqual(tester.status_code, 404)

    def test__process_data_bad_ticker(self):
        """Tests if bad ticker is provided to FinancialModelingPrep API"""
        tester = rule_one_utils.ScrapeFinancialModelingPrepJSON("123")
        self.assertEqual(tester.status_code, 404)
