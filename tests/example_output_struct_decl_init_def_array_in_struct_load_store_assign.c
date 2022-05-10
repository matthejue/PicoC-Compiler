// in:3 1 4
// expected:3 1 4 4 2 5
#include<stdio.h>

// array struct declaration
struct array_with_len {int *ar_pntr; int len;};

// fixed length array struct declaration
struct array_with_fixed_len {int ar_pntr[3]; int len;};

void main() {
  // struct initialisation with array and length
  int ar[3] = {3, 1, 4};
  struct array_with_len array = {.ar_pntr=ar, .len=3};
  int i;
  // struct definition
  struct array_with_fixed_len array2;
  // print all array elements using it's length
  i = 0;
  while (i < array.len) {
    printf(" %d", array.ar_pntr[i]);
    i = i + 1;
  }
  // copy array with all elements incremented
  array2.ar_pntr[0] = array.ar_pntr[0] + 1;
  array2.ar_pntr[1] = array.ar_pntr[1] + 1;
  array2.ar_pntr[2] = array.ar_pntr[2] + 1;
  array2.len = array.len;
  // print all array elements using it's length
  i = 0;
  while (i < array2.len) {
    printf(" %d", array2.ar_pntr[i]);
    i = i + 1;
  }
}

