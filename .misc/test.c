#include <stdio.h>

int main(int argc, char *argv[])
{
  printf("%d\n", ~0);
  printf("%d\n", ~1);
  int var = !~0;
  printf("%d\n", var);
  int var2 = ~!0;
  printf("%d\n", var2);
  return 0;
}
