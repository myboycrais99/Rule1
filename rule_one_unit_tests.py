"""
Unit testing scripts for the Rule #1 code base. Results are output to
'unittest.log'.
"""

import unittest
import rule_one_utils


# class TestBarchart(unittest.TestCase):
#
#     def test_badticker(self):
#         """Tests if a bad ticker is provided to Barchart.com"""
#         self.assertEqual(rule_one_utils.ScrapeBarchartBalanceSheetHTML(
#             "123").status_code, 404)
#
#     def test_goodticker(self):
#         """Tests if a good ticker is provided to Barchart.com"""
#         self.assertEqual(rule_one_utils.ScrapeBarchartBalanceSheetHTML(
#             "AAPL").status_code, 200)
#
#
# class TestTDAmeritrade(unittest.TestCase):
#     pass
#
#
# class TestIEXTrading(unittest.TestCase):
#     pass


# class TestFinancialModelingPrep(unittest.TestCase):
#
#     def test_goodticker(self):
#         """Tests FinancialModelingPrep's response to a good ticker symbol"""
#         self.assertEqual(rule_one_utils.ScrapeFinancialModelingPrepJSON(
#             "AAPL").status_code, 200)


if __name__ == '__main__':

    if False:
        log_file = 'unittest.log'
        with open(log_file, "w") as f:
            runner = unittest.TextTestRunner(f, verbosity=2)
            unittest.main(verbosity=2, testRunner=runner)
            f.close()
    else:
        unittest.main(verbosity=2)
