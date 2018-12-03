from unittest import TestCase
from rule_one_db import RuleOneDatabase

tester = RuleOneDatabase(host='localhost', db='rule1_devdb', user='ryan',
                         password='password')


class TestRuleOneDatabase(TestCase):
    def test__connect_db(self):
        pass



    # def test_get_big5_bad_ticker(self):
    #     """Bad ticker returns empty list."""
    #     self.assertFalse(bool(tester.get_big5(123)))
    #
    # def test_get_big5_bad_single_year_type(self):
    #     """Providing a bad year returns an empty list."""
    #     self.assertFalse(bool(tester.get_big5('AAPL', '2017a')))
    #
    # def test_get_big5_check_single_list_str(self):
    #     """List with single string for year still returns one entry."""
    #     self.assertEqual(len(tester.get_big5('AAPL', ['2017'])), 1)
    #
    # def test_get_big5_check_single_year_int(self):
    #     """List with single string for year still returns one entry."""
    #     self.assertEqual(len(tester.get_big5('AAPL', 2017)), 1)
    #
    # def test_get_big5_check_single_year_float(self):
    #     """List with single string for year still returns one entry."""
    #     self.assertEqual(len(tester.get_big5('AAPL', 2017.0)), 1)
    #
    # def test_get_big5_check_single_list_int(self):
    #     """List with single int for year still returns one entry."""
    #     self.assertEqual(len(tester.get_big5('AAPL', [2017])), 1)
    #
    # def test_get_big5_check_list_two_int(self):
    #     """List of two ints for years returns multiple entries correctly."""
    #     self.assertEqual(len(tester.get_big5('AAPL', [2015, 2017])), 3)
    #
    # def test_get_big5_check_list_int_and_str(self):
    #     """List of an int and str for years returns multiple entries correctly.
    #     """
    #     self.assertEqual(len(tester.get_big5('AAPL', [2015, '2017'])), 3)
    #
    # def test_get_big5_check_list_two_str(self):
    #     """List of two strs for years returns multiple entries correctly."""
    #     self.assertEqual(len(tester.get_big5('AAPL', ['2015', '2017'])), 3)
    #
    # def test_get_big5_bad_list_int_and_str(self):
    #     """List of an int and bad str for years returns empty list."""
    #     self.assertFalse(bool(tester.get_big5('AAPL', [2015, '2017a'])))
    #
    # def test_get_big5_check_too_many_years(self):
    #     """List of len > 2 returns empty list."""
    #     self.assertFalse(bool(tester.get_big5('AAPL', [2015, 2016, 2017])))

    def test_add_company(self):
        pass
