#include <stdio.h>

void while_true() {
  int car = 10;
  int var = 12 + (car = 12) + 1;
  printf("%d", var);
}

int main(int argc, const char **argv) { while_true(); }
