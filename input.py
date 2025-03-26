x = 10
y = 5
z = x + y * 2

print("The value of z is:", z)

def compare(a, b):
    if a > b:
        print("a is greater")
    else:
        print("b is greater or equal")

compare(x, y)

def calculate(num):
    num = num + 1
    return num

result = calculate(7)

def scopeTest(val):
    x = val
    print(x)

scopeTest(42)
print(x)
