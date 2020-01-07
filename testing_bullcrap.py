thisdict = {"apple":"green",
            "banana":"yellow",
            "cherry":"red"}

#prints the information in raw form
print(thisdict)


print()
#for loop to print the dictionary line by line

for x in thisdict:
    print(x, ':', thisdict[x])

numbers = [99, 100, 101, 102]

for n in numbers:
    print(n)

#Program 7.11


#define get_values function
def get_values():
    #create empty list
    values = []

    #loop variable
    again = 'y'

    #get values from user
    while again == 'y':
        #get num and add it to the list
        num = int(input('enter a number: '))
        values.append(num)

        #continue loop?
        print('want to add another number?')
        again = input('y = yes, anything else = no: ')
        print()

    #return the list
    return values


numbers = get_values()

print('the numbers in the list are:')
print(numbers)