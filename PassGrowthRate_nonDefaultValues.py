"""
This file looks at the growth rate percentages that are being passed
from CalcHistoricGrowthRate.py. This function returns 'true' or 'false'
if the growth rates for years: 1, 3, 5, and 9 (growth_years) are greater than
the designated 10% (exceptions)

Return TRUE If:
growth_rates > r_growth_rate AND years_failed < exceptions

return TRUE


Needs to pull in the allowed exception years from GetGrowthRateExceptions.py
That means that it'll be allowed to not pass the criteria for the designated number
of years.

Needs to pull in GROWTH RATE from GetGrowthRate.py
Needs to pull in EXCEPTION YEARS from GetGrowthRateExceptions.py
Needs to pull in GROWTH YEARS from GetGrowthYears.py

This is currently using default values for some of this stuff. 

"""

# -------------------------- Required Files----- ---------------------

#call the file GetGrowthRateExceptions2.py
#this file supplies the number of allowable years exemptions. (example: 1 allowable year
#of crappy growth rate. Default is 0, meaning every growth rate must be positive and meet
#the default 10% threshold
import GetGrowthRateExceptions2 as InputExceptions

#Call GetGrowthYears.py
#this file asks user for number of growth rate years to be calculated.
#defaults are: 1 year-delta, 5 year-delta and 9 year-delta
import GetGrowthYears as InputGrowthYears

#Call GetGrowthRate.py
#this file asks the user for the growth rate percentage that each of the year-deltas
#has to surpass in order to pass
import GetGrowthRate as InputReqGrowthRate

#call CalcHistoricGrowthRate.py
#File contains the calculated growth rate percentages for the requested years.
#This is only  test data since I don't have actual growth rate percentages
import CalcHistoricGrowthRate as InputHistoricGrowthRates


# --------------------------------------------------------------------
# --------------------------Variable Declaration ---------------------

# growth_rates:             List. It's a list of random growth rates
# pass_growth_rates:        Function. to see if the growth rates for a given stock
#                           are greater than the required_growth_rate
# required_growth_rate:     the required growth rate percentage (as an integer)
#                           to check against (default is 10%)
#
#
#
#
# --------------------------------------------------------------------

# --------------------------Function Declaration ---------------------
def main():
    print('Filename: PassGrowthRate')

    #initiate variables
    #integer for years exceptions
    exceptions = 0

    #list of growth rate percents (as integers)
    growth_rates = []

    #percent (as an integer) growth rate required to meet Rule1
    req_growth_rate = 0

    # Get Data
    exceptions, growth_rates,req_growth_rate = get_data(exceptions, growth_rates, req_growth_rate)


    # Growth Rates as integers.
    # Remember, this is bogus values since I don't have actual data yet for a given stock
    #growth_rates = InputFileGrowthRates.growth_rate_percent

    # Number of years a stock is able to fail the 10% growth rate percentage
    #exceptions = InputFileExceptions.get_years_exceptions()

    print()
    print('years exceptions in PGR =', exceptions)
    print()
    print('required growth rate in PGR = ',req_growth_rate)
    print('')
    print('growth rate percentages in PGR = ',growth_rates)
    print()

    #did the ticker pass or not
    ticker_status = pass_growth_rates(exceptions, growth_rates, req_growth_rate)







# END FUNCTION - main



#Function to get all the data imported from other files
def get_data(exceptions, growth_rates, r_growth_rate):
    # Growth Rates as integers.
    # Remember, this is bogus values since I don't have actual data yet for a given stock
    #
    growth_rates = InputHistoricGrowthRates.growth_rate_percent

    # Number of years a stock is able to fail the 10% growth rate percentage
    # single integer NUM
    exceptions = InputExceptions.get_years_exceptions()

    #Get required growth rate percentage as an integer that each year-delta must
    #surpass to be considered a Rule1 stock
    r_growth_rate = InputReqGrowthRate.main()


    return exceptions, growth_rates, r_growth_rate

#END FUNCTION get_data


def pass_growth_rates(exceptions: int, growth_rates: list, req_growth_rate: int):
    # set to default value
    # this counter counts the number of times a stock failed to meet user's desired
    # growth rate percentage
    failed_counter = 0

    print('Growth Rate Percentages: ', growth_rates)

    # Test if each spot in the list is greater than the threshold, required_growth_rate
    # all percentages should be in integers (10% -> '10')
    # if all the items in the list are greater than required_growth_rate, return TRUE
    # as soon as a value is found that's less than required_growth_rate, failed_counter
    # will increase.
    # If failed_counter > exceptions, it'll return FALSE.

    for x in growth_rates:

    # check if an item is greater than the required 10%
        if x >= req_growth_rate:
            pass
        else:
            failed_counter = failed_counter +1

        #end if
    #end for

    #check and see if a stock failed to meet the required growth rate for too many
    #years.
    if failed_counter > exceptions:
        print('this stock is allowed to not pass the 10% growth rate for,', exceptions,'years')
        print('it failed to meet the criteria')
        return False

    #it passed the criteria
    else:
        print()
        print('This stock met the requirements of a Rule1 stock.')


    return True
# End Function

#output information
def output_data(ticker_status):
    print()
    print('Did the ticker symbol pass or fail?')
    if ticker_status == True:
        print('it PASSED. It is currently a Rule1 worthy stock')

    else:
        print("it FAILED. It's not a Rule1 stock at the moment.")
        print('better luck next time')

#END FUNCTION output_data

#todo: add error handling

# --------------------------Main Declaration -------------------------

#call function
main()

#todo I think it's calling some functions twice because I'm calling the file AND then
#todo I am calling a specific function. I don't need to do both