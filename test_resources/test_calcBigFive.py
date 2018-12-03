from unittest import TestCase
import rule_one_utils
import datetime


class TestClass(rule_one_utils.CalcBigFive):
    def __init__(self, ticker: str, year: int=-1):
        rule_one_utils.CalcBigFive.__init__(self, ticker, year)

    def _calc_method1(self):
        pass

    def _calc_method2(self):
        pass

    def _calc_method3(self):
        pass


class TestCalcBigFive(TestCase):
    def test__bad_year_past(self):
        """Check for past date"""
        this_year = datetime.datetime.now().year
        tester = TestClass("AAPL")
        tester._year = this_year - 5
        tester._bad_year()
        self.assertEqual(tester._err_code, 3)

    def test__bad_year_future(self):
        """Check for past date"""
        this_year = datetime.datetime.now().year
        tester = TestClass("AAPL")
        tester._year = this_year + 5
        tester._bad_year()
        self.assertEqual(tester._err_code, 2)
