// in:42
// expected:42 42
#include<stdio.h>

void main() {
  // deref a ref
  int var = 42;
  int *pntr;
  var = *&var;
  printf(" %d", var);
  // ref a deref
  pntr = &var;
  pntr = &*pntr;
  printf(" %d", *pntr);
}

