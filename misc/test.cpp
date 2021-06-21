#include "stdio.h"

int main(int argc, const char **argv) {
  int b = 12;
  const int a = 12 + b;
  printf("%d", a);
}
