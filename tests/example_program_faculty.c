// in:3 4
// expected:6 24
#include<stdio.h>
// Author: Christoph Scholl, from the Operating Systems Lecture

int factorial(int n) {
  int res_f;
  int h;
  if (n== 1) {
    res_f = 1;
  } else {
    h = factorial(n-1);
    res_f = n * h;
  }
  return res_f;
}

void main() {
  int arg = 3;
  int res;
  printf(" %d", factorial(arg));
  res = factorial(4);
  printf(" %d", res);
}

