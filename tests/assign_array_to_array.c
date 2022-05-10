// in:42
// expected:1 42 3 1 42 3 1 42 3
#include<stdio.h>

void main() {
  int ar[3] = {1, 42, 3};
  int *ar2;
  int i;
  int *ar3;
  int ar_assign[3];
  // ---------------------------- assign to pointer ---------------------------
  // int ar2[3] = ar; doesn't work in C
  ar2 = ar;
  // print array
  i = 0;
  while (i < 3) {
    printf(" %d", ar2[i]);
    i = i + 1;
  }
  ar3 = ar;
  // print array
  i = 0;
  while (i < 3) {
    printf(" %d", ar3[i]);
    i = i + 1;
  }
  // ---------------------------- assign with loop ----------------------------
  // assign array to array
  *ar_assign = *ar3;
  i = 1;
  while (i < 3) {
    ar_assign[i] = ar3[i];
    i = i + 1;
  }
  // print array
  i = 0;
  while (i < 3) {
    printf(" %d", ar3[i]);
    i = i + 1;
  }
}

