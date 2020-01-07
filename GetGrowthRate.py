"""
This file passes the amount of growth rate a stock ticker needs to have
per year in order to be deemed 'good.' Default is 10 % growth per year

This value will be used in PassGrowthRate.py
"""

#todo: change the try/except to try/assert

# -------------------------- Required Files --------------------------
# none
#
# --------------------------------------------------------------------


# --------------------------Variable Declaration ---------------------
#growth_percent:    Int. user input. This is the desired % growth rate required
#                   of the Big Five in order for it to pass and get put on the
#                   short list of stocks to be checked weekly. Big Five calculated
#                   annually.
#growth_rate_percent: same as growth_percent
#loop_counter:      Int. it's a loop counter... just as it says.
#invalid_answer:    Int. 1 = invalid. 0 = valid
#
# --------------------------------------------------------------------
def main():
    #print filename
    print('Filename: GetGrowthRate')
    print()

    #get data
    growth_percent= get_data()

    #todo: echo the user's input and ask if that's the correct value
    #todo: if it's not the value they meant to enter, give them three attempts

    #todo: need to check if the value is an int. If it's not, exit the program

    #Check if initial input is valid
    #if the initial inputted value was not valid, ask the user for another value.
    #and check if that value is a valid number between [0,100].
    #user gets several attempts before the value is automatically set.
    growth_percent_main= echo_n_check(growth_percent)

    #Print final growth rate percent
    output_data(growth_percent_main)

    return growth_percent_main

#END FUNCTION main


#get data
def get_data():
    print('Explanation:')
    print('Growth Rate Percent is the percent growth rate a stock needs to have in \n'
          'order to be deemed GOOD. Default is 10%.')
    print('Therefore, the Big Five need to be greater than 10% for each calculated year\n'
          'for it to be considered a Rule 1 stock.\n'
          'Value needs to be between [0, 100]')
    print()
    growth_rate_percent = input('Enter desired Growth Rate Percent value as an integer: \n'
                                'Enter 10 for 10%:')

    return growth_rate_percent
#END FUNCTION get_data


#checking that the value inputted is a value number
def check_valid(num):
    #value must be between [0,100]

    if 0 < num < 100:
        return True
    else:
        return False

#END FUNCTION check_valid


#Echo user's value, check if those are desired value. If this value isn't
#desired, ask user for new a value.
def echo_n_check(answer):
    print('echo_n_check')

    #check that the value entered is the desired value
    #allow the user 3 tries to enter a value if they botched it the first time
    answer = echo_loop(answer)


    # check if value is an integer, float or char.
    # if it's an int, convert the string to int. If it's a char or float,
    # exit program after raising an exception

    answer = check_int(answer)

    print('Printing growth rate percent:', answer)

    #check that the value is in range, if it isn't... change it.
    in_range = check_valid(answer)

    #if in_range = false, answer is not between [0-100]
    #if in_range = true, answer is within range
    #if it's not in range, change it to 10% (default value)
    if not in_range:
        answer_changed = 10
        answer = answer_changed
        print("your answer is being changed since it's not in range")
        print('Growth Rate Percent:', answer)

    return answer

#END FUNCTION echo_n_check


#Offer the user several tries to input a value, otherwise Growth Rate
#will be set to default value (10) for 10%
def echo_loop(answer):
    # Set to default values
    # invalid_answer = 1: it's invalid
    # invalid_answer  =0: valid
    invalid_answer = 1

    # max number of loops = 3. Starting counter at 0.
    loop_counter = 0

    # loop if check_valid returns FALSE 3 times then a default value will be set
    # default values

    while loop_counter < 3 and invalid_answer == 1:
        print('Growth Rate Percent (integer):,', answer)
        echo_answer = input(' is this correct? "y" or "n"')

        if not check_answer(echo_answer):
            invalid_answer = 1
        elif check_answer(echo_answer):
            invalid_answer = 0

        loop_counter = loop_counter + 1

        if invalid_answer == 1:
            answer = input('Please re-enter growth rate percent.')
            print()

    # end while loop

    #If invalid_answer is still (-1) (invalid) then set to default value 10
    if invalid_answer == 1:
        answer = 10

    return answer
#END FUNCTION check_valid_loop


#checking if the user accepts the default values or not
def check_answer(answer):

    if answer == 'y' or answer == 'Y' or answer == 'yes' or answer == 'Yes' or answer == 'YES':
        return True
    else:
        return False

#END FUNCTION check_answer


def check_int(num):
    try:
        num = int(num)
        return num

    #todo: if it's not an integer, raise an exception and terminate... eventually,
    #todo: this should be logged in an error file
    #todo: Ryan is saying I should use 'assert' instead of 'except'...
    #todo: look into this a little more
    except ValueError:
        print('you did not enter a valid number. Terminating program')
        exit()
#END FUNCTION check_int


#output data function
def output_data(num):
    print()
    print('Final Growth Rate Percent:', num)
    print()
    print('End Function')

#END FUNCTION output_data


#Call function
main()