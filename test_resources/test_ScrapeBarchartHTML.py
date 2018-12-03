from unittest import TestCase
import rule_one_utils


tester_ip = "192.168.1.12"


class TestScrapeBarchartHTML(TestCase):

    def test__process_good_data(self):
        """Tests if a good ticker is provided to Barchart.com"""
        tester = rule_one_utils.ScrapeBarchartHTML("AAPL")
        tester._data = {}
        tester._url = "http://{}/test_resources/barchart_good.html"\
                      "".format(tester_ip)
        tester._fetch_data()
        tester._process_data()
        self.assertEqual(tester.status_code, 200)

    def test__process_data_bad_ticker_type(self):
        """Test if Barchart.com scraper handles wrong ticker type"""
        tester = rule_one_utils.ScrapeBarchartHTML(123)
        self.assertEqual(tester.status_code, 404)

    def test__process_data_bad_ticker(self):
        """Test if Barchart.com scraper handles a bad ticker"""
        tester = rule_one_utils.ScrapeBarchartHTML("123")
        self.assertEqual(tester.status_code, 404)

    def test__process_data_bad_value(self):
        """Test if Barchart.com scraper handles bad data"""
        try:
            tester = rule_one_utils.ScrapeBarchartHTML("AAPL")
            tester._url = ("http://{}/test_resources/"
                           "barchart_bad_value.html".format(tester_ip))
            tester._data = {}
            tester._fetch_data()

        except ValueError as e:
            self.fail("Failed with error '{}'".format(e))

    def test__fetch_no_redirect(self):
        tester = rule_one_utils.ScrapeBarchartHTML("WPXP")
        self.assertEqual(tester.status_code, 302)

    # TODO - Define test for less than five years of data

    # TODO - "FAX" Returns 'None' for Beautifulsoup data.
