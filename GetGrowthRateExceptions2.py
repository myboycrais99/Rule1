"""
Date: 7 July 2019

This file passes the maximum allowed number of years that the stock
is allowed to fail to meet the desired growth rates. Default is 0 years

This value will be used in PassGrowthRate.py
"""
#todo: need to verify valid user data (pull function from GetGrowthYears.py)
#todo: ensure to echo user input...this is happening but even when I say "yes"

# -------------------------- Required Files----- ---------------------
# none
#
# --------------------------------------------------------------------


# --------------------------Variable Declaration ---------------------

# years:                global variable
# years_exceptions:     This is the maximum allowed number of years that
#                       the stock is allowed to fail to meet the desired
#                       growth rates.
# loop_counter:         used for the while loop.
# invalid_answer:       boolean expression... 0 is valid. 1 is invalid.
# get_years_exceptions: function to get data.
# check_valid:          function to check valid number.
# check_valid_loop:     function to offer user 3 tries to submit valid number
#                       otherwise, years_exceptions set to default value
# output_data:          function to output data
# --------------------------------------------------------------------
def main():
    # print filename
    print('Filename: GetGrowthRateExceptions')

    # default value
    years = 0

    print()

    print(
        'Years Exceptions: Number of years a stock is allowed to fail the Big Five '
        'and still be deemed a Rule1 stock. For example, if there was a recession in '
        'a given year, that might be grounds for exempting that year. User would '
        'specify 1 to indicate one bad year is allowed and a stock is still deemed '
        'a Rule1 stock.')

    print()

    print(
        'Please enter an integer between [0,5] indicating a stock is allowed to '
        'fail the Big Five between one and five years.')

    print()

    # set variable equal to 'years_exceptions' variable being returned from function
    # get_years_exceptions
    years = get_years_exceptions()

    # todo: need to echo the value and ask if that was correct here
    #todo: the echo_loop function should be copied over from GetGrowthYears.py
    #todo: this shouldn't be in the main function... silly Kim

    # echo the data entered and repeat the get_data if necessary
    ans_echo_data = echo_data(years)

    #checking if the user accepts his or her input
    #invalid_answer = 0 -- answer is accepted
    #invalid_answer = 1 -- user rejects the value and needs to input a new value
    if not check_answer(ans_echo_data):
        invalid_answer = 1

    elif check_answer(ans_echo_data):
        invalid_answer = 0
        print('Year Exceptions: ', years)
        print('terminating the program. Have a great day :)')
        exit()


    # while loop: this should look at the function for checking if
    # user input is "y" "YES" "Yes" "YEs" etc...
    while True:
        years = get_years_exceptions()
        print()
        ans_echo_data = echo_data(years)
        print()
        if ans_echo_data == 'y': #<- same comment as above
            break

    # Check if initial value is valid.
    # if the initial inputted value was not valid, ask the user for another value.
    # and check if that value is a valid number between [0,5].
    # user gets several attempts before the value is automatically set.
    years_exceptions_main = check_valid_loop(years)

    # output years exceptions
    output_data(years_exceptions_main)


# END FUNCTION Main

# This function requests the user to input a value. If an invalid answer is supplied, it
# allows the operator three attempts before it sets the default value
def get_years_exceptions():
    years_exceptions = input(
        'Maximum allowed number of years that a stock is allowed '
        'to fail to meet the desired growth rates: ')

    print()

    # converting value to an integer
    years_exceptions = int(years_exceptions)

    return years_exceptions


# END FUNCTION get_years_exceptions

# echo the data
def echo_data(num):
    print("you entered:", num)
    ans_echo = input("is this correct? 'y' or 'n':")
    print()

    return ans_echo


# END FUNCTION echo_data

# checking that the value inputted is a meets requirements
def check_valid(num):
    # value must be between [0,5]

    if num >= 0 and num <= 5:
        return True
    else:
        return False


# END FUNCTION check_valid

# Offer the user several tries to input a valid number, otherwise years_exceptions
# will be set to a default value
def check_valid_loop(years_exceptions):
    # Set to default values
    # invalid_answer = 1: it's invalid
    # invalid_answer  =0: valid
    invalid_answer = 1

    #todo: need the echo loop

    # max number of loops = 3. Starting counter at 0.
    loop_counter = 0

    # loop if check_valid returns FALSE 3 times then a default value will be set
    # default value is years_exceptions = 0.
    while loop_counter < 3 and invalid_answer == 1:
        if check_valid(years_exceptions) == False:
            invalid_answer = 1
        elif check_valid(years_exceptions) == True:
            invalid_answer = 0

        loop_counter = loop_counter + 1

        if invalid_answer == 1:
            years_exceptions = int(input(
                'You entered an invalid answer. Please try again: '))

        # end while loop

        # Check the final looped value was valid or not
        if loop_counter == 3 and invalid_answer == 1:
            if check_valid(years_exceptions) == False:
                invalid_answer = 1

            elif check_valid(years_exceptions) == True:
                invalid_answer = 0

        # end if

        # Check if loop_counter = 4. If it does, set the years_exception to default value 0
        if loop_counter == 3 and invalid_answer == 1:
            years_exceptions = 0
            print()
            print()
            print(
                'you suck as you apparently can not follow the simplest of instructions.')
            print('I am overriding your answer to 0')
            print()

    # since inputs are always as a string, this function converts it to an integer
    years_exceptions = int(years_exceptions)

    return years_exceptions


# END FUNCTION check_valid_loop


#checking if the user accepts the default values or not
def check_answer(answer):

    if answer == 'y' or answer == 'Y' or answer == 'yes' or answer == 'Yes' or answer == 'YES':
        return True
    else:
        return False

#END FUNCTION check_answer


# Function to print data
def output_data(years_except):
    print('allowed years exceptions:', years_except)
    print()
    print('end function')


# END FUNCTION output_data

# call the functions
main()

# todo: instead of printing a nice message, the values that pass the criteria need to
# todo: then move on to another list or be exported etc.
# todo: should echo the value and then ask if the value entered was the correct value
