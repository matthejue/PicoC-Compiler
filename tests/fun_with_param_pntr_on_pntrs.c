// in:1 2 3 4
// expected:1 2 3 4
#include<stdio.h>

void connect(int **pntr, int (*ar)[2], int len);

void main() {
  int *pntr[2];
  int ar[2][2] = {{1, 2}, {3, 4}};
  int len_ar = 2;
  int len_pntr = 4;
  int i;
  connect(pntr, ar, len_ar);
  i = 0;
  while (i < len_pntr) {
    printf(" %d", (*pntr)[i]);
    i = i + 1;
  }
}

void connect(int **pntr, int (*ar)[2], int len) {
  int i = 0;
  while (i < len) {
    pntr[i] = ar[i];
    i = i + 1;
  }
}

