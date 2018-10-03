'''
This file looks at the growth rate percentatges that are being passed
from CalcHistoricGrowthRate.py. This function returns 'true' or 'false'
if the growth rates for years: 1, 3, 5, and 9 are greater than
the designated 10%

Needs to pull in the allowed exception years from GetGrowthRateExceptions.py
That means that it'll be allowed to not pass the criteria for the designated number
of years.

'''

# -------------------------- Required Files----- ---------------------

#call the file GetGrowthRateExceptions.py
#this file supplies the number of allowable years exemptions. (example: 1 allowable year
#of crappy growth rate. Default is 0, meaning every growth rate must be positive and meet
#the default 10% threshold
import GetGrowthRateExceptions as InputFileExceptions

#call CalcHistoricGrowthRate.py
#File contains the calculated growth rate percentages for the requested years
import CalcHistoricGrowthRate as InputFileGrowthRates




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

# Growth Rates as integers
growth_rates = InputFileGrowthRates.growth_rate_percent

# Number of years a stock is able to fail the 10% growth rate percentage
exceptions = InputFileExceptions.years_exceptions

print()
print('years exceptions in PGR =', exceptions)
print()
# required growth rate that all values in the list must be greater than. Default is 10%
# shown as an integer (10% -> 10)
required_growth_rate = 10

print()
print('Filename: PassGrowthRate')

def pass_growth_rates(growth_rates: list, required_growth_rate: int):
    # set to default value
    # this counter counts the number of times a stock failed to meet 10% growth rate
    failed_counter = 0

    print('Growth Rate Percentages: ', growth_rates)

    # Test if each spot in the list is greater than the threshold, required_growth_rate
    # required_growth_rate currently set to 10%
    # all percentages should be in integers (10% -> '10')
    # if all the items in the list are greater than 10%, return TRUE
    # as soon as a value is found that's less than 10%, it'll return FALSE and
    # kick out of the function.

    for x in growth_rates:

        # check if an item is greater than the required 10%
        if x >= required_growth_rate:
            print('passed')

        else:
            print('return False')
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
        print('true. All values are greater than 10% growth rate')


    return True
# End Function



#Calling the function to check if the growth rate percentages pass the threshold
#Treshold is required_growth_rate
#If it passes 'TRUE' then print a message
#If it fails, print a different message
# if (pass_growth_rates(growth_rates, required_growth_rate)== True):
#     print()
#     print('yay, it passes the test')
#     print()
# else:
#     print()
#     print('sucky')
#     print()


#todo: add error handling