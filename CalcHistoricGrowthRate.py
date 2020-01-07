"""
This file calculates Growth Rate Percentages. It requires
the following to be sent to it:
1. a dictionary containing years and Sales, Equity or some other value
    (in Millions of dollars)
    It requires the values to be sent in the form: Year, Sales

2. years-delta requested (example: 1, 3, 10 for 1 year delta, 3 year delta etc

Output:
It will output a list of percentages representing the percent growth rate
for the requested years

The growth rate percentages are used in PassGrowthRate_nonDefaultValues.py

Step 2c:
unit-test the function program by writing a 'main' file to call the function

todo: clean up the program. add param: where appropriate.
todo: create a log file and send warnings when there's bad data.
todo: learn classes and use them appropriately.

"""
# -------------------------- Required Files----- ---------------------
# Test_Data_Send_to_CalcHistoricGrowthRate.py
# Above file contains the years and numbers (in millions) that this file
# will calculate growth rates on.

#call the file Test_Data_Send_to_CalcHistoricGrowthRate.py
import Test_Data_Send_to_CalcHistoricGrowthRate as InputFile

#
#
# --------------------------------------------------------------------
# --------------------------Variable Declaration ---------------------

# equity_raw_data:              Dictionary. containing years and the equity (in Millions)
# total_growth_rate_percent:    Double. 3yr growth rate
# yearly_growth_rate_percent:   Double. yearly growth rate (total GRP / total years)
# growth_rate_years:            Int. total years of equity data collected
# growth_rate_funct:            Function.
#                               Inputs: dictionary of 10 years and 10 values
#                                   list of years requested example: [1,3,5]
#                               Outputs: list of requested growth rate percentages. Ex: [6.42, 12.72, 20.17]
# list_data:                    equity_raw_data -> in function
# list_years:                   requested_years -> in function
# growth_rate_percent:          List. containing the interested growth rate percentages
#                               for the requested year-deltas.
# --------------------------------------------------------------------

# total equity, sales or whatever number (in Millions) for a given year.
# this information is in the form: {year: value (in millions)}
#EXAMPLE DATA
# equity_raw_data = {2014: 111547, 2015: 119355, 2016: 128249, 2017: 134047}

def main():
    raw_data = InputFile.equity_raw_data

    from datetime import date           #needed to use the date built-in functions

    # list containing the year-deltas for the growth rate percentages
    # example: [1, 3, 10] meaning the user requests the 1, 3, and 10 year growth rate percentages
    years_requested = InputFile.years_requested

    # defining last full year of data collected. It'll always be one year less than today's year
    today_date = date.today()           #getting today's date
    year_now = today_date.year          #getting actual year it is now
    current_year: int = year_now - 1    #getting last year of data collected

    print('Filename: CalcHistoricGrowthRate')
    print()
    print('Equation for Growth Rate: [Ending Balance/Beginning Balance]^(1/n)-1')
    print('n = number of years')
    print()
    print('Total in Millions of Dollars:')

    print()

    # Print each row of Dictionary 'raw_data'
    for x in raw_data:
        print(x, ": $", raw_data[x])

    # Pass information to a function to calculate growth rate percent and return a value
    # need to pass the dictionary with years and Equity or other value in Millions of Dollars
    # also need to pass current year (int) and requested years (list)
    # returns a list of the requested % growth rates
    print()

    # Call Function
    growth_rate_percent = growth_rate_funct(raw_data, years_requested, current_year)

    # print the list of growth rates
    print(growth_rate_percent)


#END MAIN FUNCTION

#------ Function Definitions -------------#

def growth_rate_funct(list_data: dict, list_years: list, current_year: int) -> list:
    #defining function parameters
    #create list of growth rate percentages that are being requested
    growth_rate_percent = []

    #this is the calculated value to be appended to the list
    growth_rate_p = 0.0


    print('Function: Calculate Percent Growth Rate:')
    print('requested delta-years', list_years)
    print()

    # loop to calculate the growth rate for each requested year
    for x in list_years:
        print("year-delta: ", x)
        interested_year = current_year - x
        list_data.get(interested_year)

        #Calculate growth rate percentage
        # Equation for Growth Rate: [Ending Balance / Beginning Balance] ^ (1 / n) - 1
        # n = number of years
        #growth_rate_p = (list_data.get(current_year) - list_data.get(
        #    interested_year)) / list_data.get(interested_year) * 100

        growth_rate_p = ((list_data.get(current_year) / list_data.get(
            interested_year)) ** (1/(current_year - interested_year)) -1)*100


        #round number to 2 decimal places
        growth_rate_p = round(growth_rate_p, 2)

        #append the number, growth_rate_p to the list
        growth_rate_percent.append(growth_rate_p)

        #Print Growth Rates in the list
        print('Growth Rate Percent: ', growth_rate_p, '%')
        print()

        #End For Loop

    #return the list of growth rate percentages
    return growth_rate_percent


# END FUNCTION


#Call Main Function
main()

# todo add error flagging code in the function
