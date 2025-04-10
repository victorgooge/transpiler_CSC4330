// Variables and arithmetic
let x = 10;

let y = 5;

let z = ((x * y) + 2);

console.log('z:', z);

// Function and return
function add(a, b) {
  let result = (a + b);
  return result;
}

let sum_val = add(x, y);

console.log('sum:', sum_val);

// If/else conditional
if (x > y) {
  console.log('x is greater');
} else {
  console.log('y is greater or equal');
}

// For loop with list
let numbers = [1, 2, 3];

for (let n of numbers) {
  console.log(n);
}

// While loop
let count = 0;

while (count < 3) {
  console.log('counting:', count);
  count = (count + 1);
}

// Data structures
let my_list = [10, 20, 30];

let my_tuple = [1, 2];

let my_set = new Set([3, 4, 5]);

let my_dict = {'a': 1, 'b': 2};

// Access data
console.log(my_list);

console.log(my_tuple);

console.log(my_set);

console.log(my_dict);

// Match statement (Python 3.10+)
function respond(status) {
  switch (status) {
    case 'ok':
      console.log('Everything is fine');
      break;
    case 'error':
      console.log('Something went wrong');
      break;
    default:
      console.log('Unknown status');
      break;
  }
}

respond('ok');

respond('error');

respond('idk');

/*
 * Testing with
 * mulit-line comments.
 */