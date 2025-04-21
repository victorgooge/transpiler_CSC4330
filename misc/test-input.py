# This is a one-line comment

"""
This is a multi-line comment
that should become a block comment
in JavaScript output.
"""

# Loops with range()
arr = [1, 2, 3, 4, 5]
for i in range(len(arr)):
    arr[i] += 1
    if i == len(arr) - 1:
        break
    else:
        continue

# For-each loop
names = ["Alice", "Bob", "Charlie"]
for name in names:
    print(name)

# Range with single argument
for i in range(3):
    print(i)

# Range with start and stop
for i in range(2, 5):
    print(i)

# Range with step
for i in range(0, 10, 2):
    print(i)

# If/elif/else
n = 3
if n == 1:
    print("One")
elif n == 2:
    print("Two")
else:
    print("Something else")

# Function definition
def greet(name):
    print("Hello", name)
    return name + "!"

greet("Victor")

# Tuple unpacking
point = (10, 20)
x, y = point
print(x)
print(y)

# List comprehension
squares = [x * x for x in range(5)]
print(squares)

# Augmented assignments
a = 5
a += 2
a -= 1
a *= 3
a /= 2
print(a)

# PEMDAS precedence
result = 2 + 3 * 4 ** 2 / (1 + 1)
print(result)

# match-case (switch)
lang = "JavaScript"

match lang:
    case "Python":
        print("Interpreted")
    case "JavaScript":
        print("Dynamic")
    case _:
        print("Unknown")

# None and Boolean
status = None
flag = True
if not flag and status is None:
    print("All good")
