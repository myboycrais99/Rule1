from unittest import TestCase
import numpy as np
from rule_one_utils import StockScrapper


class TestStockScrapper(TestCase):
    def test__multiple_replace(self):
        """Test that all bad characters are removed from string"""
        tester = StockScrapper("AAPL")
        d = {"$": "", ",": ""}
        s = "$1,000,000"
        self.assertEqual(tester._multiple_replace(s, d), "1000000")

    def test__make_num_good_num(self):
        """Test that _make_num returns number when a good string is provided."""
        tester = StockScrapper("AAPL")
        self.assertEqual(tester._make_num("1000", int), 1000)

    def test__make_num_bad_num(self):
        """Test that _make_num returns np.NaN when a bad string is provided."""
        tester = StockScrapper("AAPL")
        self.assertTrue(np.isnan(tester._make_num("--", int)))
