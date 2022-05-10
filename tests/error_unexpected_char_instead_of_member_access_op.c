// in:
// expected:UnexpectedCharacter
#include<stdio.h>

struct point {int x; int y;};

void main() {
  struct point p1 = {.x=4, .y=2};
  printf(" %d", p1::x);
}

