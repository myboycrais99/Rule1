'''
This file passes the maximum allowed number of years that the stock
is allowed to fail to meet the desired growth rates. Default is 0 years

This value will be used in PassGrowthRate.py
'''

# -------------------------- Required Files----- ---------------------
#
#
# --------------------------------------------------------------------


# --------------------------Variable Declaration ---------------------

# years:                global variable
# years_exceptions:     This is the maximum allowed number of years that
#                       the stock is allowed to fail to meet the desired
#                       growth rates.
# loop_counter:         used for the while loop.
# invalid_answer:       boolean expression... 0 is valid. 1 is invalid.
#
# --------------------------------------------------------------------

#default value
years_exceptions = 0

print()
#print filename
print('Filename: GetGrowthRateExceptions')

#This function requests the user to input a value. If an invalid answer is supplied, it
#allows the operator three attempts before it sets the default value
def get_years_exceptions ():


    # years_exceptions = input('Maximum allowed number of years that a stock is allowed '
    #                      'to fail to meet the desired growth rates: ')
    # print()
    #
    #
    # #Set to default values
    # #invalid_answer = 1: it's invalid
    # #invalid_answer  =0: valid
    # invalid_answer = 1
    #
    # # max number of loops = 3. Starting counter at 0.
    # loop_counter = 0
    #
    # #Check if the value is a number below 5. If it's not, ask for a new value.
    # #Allow for three attempts before setting default value to 0.
    # while loop_counter <= 3 and invalid_answer == 1:
    #
    #     if years_exceptions == '0':
    #         invalid_answer = 0                  #0 means it's valid
    #     elif years_exceptions == '1':
    #         invalid_answer = 0
    #     elif years_exceptions == '2':
    #         invalid_answer = 0
    #     elif years_exceptions == '3':
    #         invalid_answer = 0
    #     elif years_exceptions == '4':
    #         invalid_answer = 0
    #     else:
    #         years_exceptions = input('You entered an invalid answer. Please try again: ')
    #
    #         loop_counter = loop_counter + 1
    #
    # #end while loop
    #
    #     #Check the final looped value was valid or not
    #     if loop_counter == 4 and invalid_answer == 1:
    #         if years_exceptions == '0':
    #             invalid_answer = 0                  #0 means it's valid
    #         elif years_exceptions == '1':
    #             invalid_answer = 0
    #         elif years_exceptions == '2':
    #             invalid_answer = 0
    #         elif years_exceptions == '3':
    #             invalid_answer = 0
    #         elif years_exceptions == '4':
    #             invalid_answer = 0
    #     #end if
    #
    #     # Check if loop_counter = 4. If it does, set the years_exception to default value 0
    #     if loop_counter == 4 and invalid_answer == 1:
    #         years_exceptions = 0
    #         print()
    #         print()
    #         print('you suck as you apparently can not follow the simplest of instructions.')
    #         print('I am overriding your answer to 0')
    #         print()
    #         print('years exceptions: ', years_exceptions)
    #
    # #since inputs are always as a string, this function converts it to an integer
    # years_exceptions = int(years_exceptions)
    #
    # print()
    # print('years exceptions: ', years_exceptions)

    #temporarily overriding years exceptions to a default value for troubleshooting
    years_exceptions = 1
    print('years excempt:', years_exceptions)
    return years_exceptions

# END FUNCTION

#call the function
get_years_exceptions()

#outside_funcion_exceptions = get_years_exceptions()

#print()
#print('final answer \n years exceptions =', outside_funcion_exceptions)


#todo: instead of printing a nice message, the values that pass the criteria need to
#todo: then move on to another list or be exported etc.