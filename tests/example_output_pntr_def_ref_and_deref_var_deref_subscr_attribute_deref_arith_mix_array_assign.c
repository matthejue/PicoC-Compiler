// in:21 3
// expected:21 3 3 3 3 42
#include<stdio.h>

struct array_with_len {int *ar; int len;};

void main() {
  // pointer definition
  int *pntr_on_int;  // pointer on integers
  int **pntr_on_pntr;  // pointer on pointers
  // reference and dereference operator on variable
  int var = 21;
  int ar[3] = {4, 2, 3};
  struct array_with_len st_ar = {.ar=ar, .len=3};
  pntr_on_int = &var;
  printf(" %d", *pntr_on_int);
  // reference operator on a dereference operation
  pntr_on_int = &*(ar + 1 + 1);
  printf(" %d", *pntr_on_int);
  // reference operator on a subscript operation
  pntr_on_int = &ar[1 + 1];
  printf(" %d", *pntr_on_int);
  // reference operator on a attribute operation
  pntr_on_pntr = &st_ar.ar;
  printf(" %d", *(*pntr_on_pntr + st_ar.len - 1));
  // pointer mixed with array
  printf(" %d", *(pntr_on_pntr[0] + 2));
  // assignment to deref
  *pntr_on_int = var * 2;
  printf(" %d", ar[2]);
}

