# Variables and arithmetic
x = 10
y = 5
z = x * y + 2

print("z:", z)

# Function and return
def add(a, b):
    result = a + b
    return result

sum_val = add(x, y)
print("sum:", sum_val)

# If/else conditional
if x > y:
    print("x is greater")
else:
    print("y is greater or equal")

# For loop with list
numbers = [1, 2, 3]
for n in numbers:
    print(n)

# While loop
count = 0
while count < 3:
    print("counting:", count)
    count = count + 1

# Data structures
my_list = [10, 20, 30]
my_tuple = (1, 2)
my_set = {3, 4, 5}
my_dict = {"a": 1, "b": 2}

# Access data
print(my_list)
print(my_tuple)
print(my_set)
print(my_dict)

# Match statement (Python 3.10+)
def respond(status):
    match status:
        case "ok":
            print("Everything is fine")
        case "error":
            print("Something went wrong")
        case _:
            print("Unknown status")

respond("ok")
respond("error")
respond("idk")

'''
Testing with
mulit-line comments.
'''