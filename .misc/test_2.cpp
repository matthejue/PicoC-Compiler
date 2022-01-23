#include <stdio.h>

int main() {
  int car = 10;
  const char var = car = 2147483647;
  printf("%c", var);
}
