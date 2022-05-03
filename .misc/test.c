#include <stdio.h>

int main(int argc, char *argv[])
{
  struct point {int x; int y;};
  struct point a[2] = {{.x=12, .y=13}, 1};
  printf("%d", a[0].x);
  printf("%d", a[0].y);
  printf("%d", a[1].x);
  printf("%d", a[1].y);
  int var[] = {10, 11, 12};
  int *var2 = 10;
  return 0;
}
