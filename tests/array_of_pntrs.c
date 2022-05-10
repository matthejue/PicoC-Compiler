// in:42
// expected:42 42 42 42 42 42
#include<stdio.h>

void main() {
  int var = 42;
  int ar[3] = {1, var, 3};
  // array of pointers
  int *ar_of_pntrs[3];
  ar_of_pntrs[0] = ar;
  ar_of_pntrs[1] = &ar;
  ar_of_pntrs[2] = &var;
  printf(" %d", ar_of_pntrs[0][1]);
  // the subtype of the array decides how the 2nd subscript behaves:
  printf(" %d", ar_of_pntrs[1][1]);
  printf(" %d", ar_of_pntrs[2][0]);
  printf(" %d", *(*ar_of_pntrs + 1));
  printf(" %d", *(*(ar_of_pntrs + 1) + 1));
  printf(" %d", **(ar_of_pntrs + 2));
}

