#include <stdio.h>

void main() {
  int var = 12;
  int car = *&var;
  printf("\n%d", var);
  printf("\n%d", car);
  // int ar[3] = {1, 3, 4};
  // printf("\n%d", *(ar+1+1));
  // // pointer definition
  // // pointer on integers
  // int *pntr_on_int;
  // // pointer on arrays of size 3
  // int (*pntr_on_array)[3];
  // // reference operator on variable
  // int var = 42;
  // pntr_on_int = &var;
  // printf("\n%d", *pntr_on_int);
  // // reference operator on a dereference operation
  // int ar[3] = {1, 2, 3};
  // pntr_on_int = &*(a + 1);
  // // reference operator on a subscript operation
  // // &*ar[1];
  // // reference operator on a attribute operation
  // // pointer arithmetic
  // pntr_on_int = &*ar;
  // // same as just 'ar' as 'ar' has the datatype 'array of int' = 'pointer of
  // // int' in the symbol table, the value is the address of the first element
  // printf("\n%d", *(pntr_on_int + 1));
  // pntr_on_array = &ar;
  // printf("\n%d", *(*pntr_on_array + 1));
  // // pointer mixed with array
  // // complex assignment to ref
}
