// in:42
// expected:42
#include<stdio.h>

void main() {
  int var = 42;
  int *ar[2];
  *(ar + 1) = &var;
  // the subtype of the array decides if the deref works
  printf(" %d", **(ar + 1));
}

