// in:10 10
// expected:10 11
#include<stdio.h>

void main() {
  // variable initialisation
  int var = 0;
  // constant initialisation
  const char var_const = 1;  // single line comment
  /* multi
  line
  comment */
  // while
  while(var < 10) {
    var = var + 1;
  }
  printf(" %d", var);
  // do while
  do {
    var = var + var_const;
  } while(var < 10);
  printf(" %d", var);
}

