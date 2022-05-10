// in:41
// expected:24 42
#include<stdio.h>

void main() {
  // complex initialisation
  int var = 41 + 1;
  // variable definition, char datatype
  char var2;
  int i = 1;
  // if, else if, else in combinatin with while
  while (i <= 2) {
    if (var > 100) {
      var2 = 0;
    } else if (var > 42 / /* inline comment */ i) {
      // nested if
      // if, if else without else
      if (0 && 1) {
        var2 = 1;
      } else if (var + 10) {
        var2 = 42;
      }
    } else
      var2 = 24;
    // several if after another
    if (4 + 2 || 0) {
      printf(" %d", var2);
    } else {
      // else with braces
      // empty else
    }
    i = i + 1;
  }
}

