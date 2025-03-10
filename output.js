let x = 100;
let y = 5;
  console.log((x * y));
function evalNums(a, b) {
  if (x > y) {
  console.log('yuhhh');
  } else {
  console.log('nahhh');
  }
}
evalNums(x, y);
x = 0;
evalNums(x, y);

function printANum(num) {
  x = num;
  console.log(x);
}
printANum(42);
console.log(x)