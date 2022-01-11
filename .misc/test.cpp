#include <stdio.h>

int main() {
  printf("%d\n", 1 > 0 && 0 + 10);
  printf("%d\n", 1 > 0 && 0 + 10 < 5);
  printf("%d\n", (1 > 0 && 1) + 10);
  printf("%d\n", 1 > 0 + 10);
  printf("%d\n", 10 && 0 + 10 > 0);
  printf("%d\n", 10 < 0 && 0 + 10);
  printf("%d\n", 1 < 1 + (3 < 9));
  printf("%d\n", (1 < 10) + (3 < 9));
  if ('c')
    if (true) {;;;};;;
}
