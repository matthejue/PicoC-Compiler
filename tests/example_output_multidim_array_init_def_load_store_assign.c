// in:3 2 1
// expected:5 42
#include<stdio.h>

void main() {
  // multidimensional array initialisation
  int var[2][3] = {{1, 2, 3},{1, 2 + 3, 3}};
  // array definition
  int var2[2];
  // array store
  var2[0] = 2;
  // array_load
  printf(" %d", var[1][2 - 1]);
  // array load + store, complex array assign
  var2[1] = var[1][2 - 1] * 8;
  // final result
  printf(" %d", var2[0] + var2[1]);
}

