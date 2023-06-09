number_of_iterations = input("Enter number of values to be input:")
number_of_iterations = int(number_of_iterations)
list_entries = []
for x in range(number_of_iterations):
    list_entries.append(int(input(f"{x}. Enter the number:")))

print(f'The sum is {sum(list_entries)}')
print(f'The smallest values of entered numbers is {min(list_entries)}')
