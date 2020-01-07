'''
This file passes a list of growth rates to the file PassGrowthRate.py
and checks if a 'TRUE' or 'FALSE' statement is returned from the file.
If PassGrowthRate.py returns 'TRUE' that means that the Big Five were all greater
than 10% growth rate.
'''

# -------------------------- Required Files----- ---------------------
# PassGrowthRate.py

#call the file PassGrowthRate.py
import PassGrowthRate as PassGrowthRate
#
#
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
#print filename
print()
print('Filename: CallingPassGrowthRate')
#defining the growth rate percentages
#defining the required growth rate percentages
growth_rates= PassGrowthRate.growth_rates
required_growth_rate = 10

#call the function from file PassGrowthRate.py
#if it passes "TRUE" then print a nice message.
#If it returns 'FALSE', print something else
if  PassGrowthRate.pass_growth_rates(growth_rates, required_growth_rate)== True:
    print()
    print('yay, it passes the test. - I called this from another file')
else:
    print()
    print('sucky - I called this from another file')


#todo: instead of printing a nice message, the values that pass the criteria need to
#todo: then move on to another list or be exported etc.