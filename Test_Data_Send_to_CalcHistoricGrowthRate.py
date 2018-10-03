'''
This file is just for practice. It needs to be removed later.

this file will contain information (years and Equity) to be sent to CalcHistoricGrowthRate.py
CalHistoricGrowthRate.py then calculates the Growth Rate Percentages for the requested
years. That information is then sent to PassGrowthRate.py when sends a 'TRUE'
or 'FALSE' if all the percentages meet the default criteria.

Test_Data -> CalcHistoricGrowthRate -> PassGrowthRate -> CallingPassGrowthRate

'''

# --------------------------Variable Declaration ---------------------

# equity_raw_data:      Dictionary. {Year, Equity}
# years_requested:      List. year-deltas for the calculation to be ran on
#
#

# --------------------------------------------------------------------

# total equity (in Millions) for a given year.
# {2014: 111547, 2015: 119355, 2016: 128249, 2017: 134047}
equity_raw_data = {2014: 111547, 2015: 119355, 2016: 128249, 2017: 10000}


# list containing the year-deltas for the growth rate percentages
# example: [1, 3, 10] meaning the user requests the 1, 3, and 10 year growth rate percentages
years_requested = [1, 2, 3]



#todo: this is only test data to send to the other function. Later, it should be
#todo: replaced with legit data.