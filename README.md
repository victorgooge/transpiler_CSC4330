# Python to JavaScript Transpiler

A simple transpiler that converts Python code to equivalent JavaScript code.

## Quick Start

1. Place your Python code in `input.py`
2. Run the transpiler:
   ```bash
   python transpiler.py
   ```
3. Get your JavaScript code from `output.js`

## Project Structure

Required files:
- `transpiler.py` - Main transpiler implementation
- `input.py` - Your Python code to transpile

## Supported Features

### Core Language Features
- Variables and assignments
- Basic arithmetic operations (+, -, *, /, %, **)
-  Comparison operators (==, !=, <, >, <=, >=)
- Logical operators (and, or, not)
- If-elif-else statements with proper nesting
-  For loops with:
  - range() support
  - iterable support
- While loops
- Function definitions and calls
- Comments (both single-line and multi-line)

### Data Types & Operations
- Numbers (integers and floats)
- Strings with:
  - f-strings
  - Basic format specifiers (.2f)
  - Template literals
- Lists with:
  - Basic operations
  - Array indexing
  - List comprehensions
- Dictionaries (basic key-value operations)

### Built-in Functions & Methods
- len() → .length
- range() → Array.from
- print() → console.log()

### List Methods
- append() → push()
- extend() → push()
- remove() → splice()
- pop() → pop()
- clear() → length = 0
- index() → indexOf()
-  sort() → sort()
- reverse() → reverse()

## Limitations

### Unsupported Features
- Classes and object-oriented features
- Complex pattern matching in match statements
- Advanced string format specifiers
- Python standard library functions
- Exception handling (try/except)
- Decorators
- Generators and yield statements
- Context managers (with statements)
- Multiple assignment (a, b = 1, 2)
- Complex slicing operations
- Set and tuple data types

## Example

Input (`input.py`):
```python
def calculate_stats(numbers):
    if not numbers:
        return 0, 0, 0  # min, max, avg for empty list
    
    current_sum = 0
    current_min = numbers[0]
    current_max = numbers[0]
    
    for num in numbers:
        current_sum += num
        if num < current_min:
            current_min = num
        elif num > current_max:
            current_max = num
    
    average = current_sum / len(numbers)
    return current_min, current_max, average
```

Output (`output.js`):
```javascript
function calculate_stats(numbers) {
  if (!numbers) {
    return [0, 0, 0];
  }
  let current_sum = 0;
  let current_min = numbers[0];
  let current_max = numbers[0];
  
  for (let num of numbers) {
    current_sum += num;
    if (num < current_min) {
      current_min = num;
    } else if (num > current_max) {
      current_max = num;
    }
  }
  
  let average = current_sum / numbers.length;
  return [current_min, current_max, average];
}
```
