#include <stdio.h>

void while_true() {
  int car = 10;
  int var = 12 && 13 || 12;
  printf("%d", var);
}

int main(int argc, const char **argv) { while_true(); }
