// in:42
// expected:1 2 3 4 5 6 42 1 2 3 4 5 6 3 -1
#include<stdio.h>

struct array_with_len {int ar[3]; int len;};

void print_all(int i, int ar[3], struct array_with_len st_ar_copy);

int print_all_pntr(int *len_ref, int *ar_ref, struct array_with_len *st_ar_ref);

void main() {
  // fun_call as statement
  int ar[3] = {1, 2, 3};
  struct array_with_len st_ar = {.ar={4, 5, 6}, .len=3};
  int len;
  int success;
  print_all(3, ar, st_ar);
  printf(" %d", ar[2]);
  // fun_call as expression
  len = 3;
  success = print_all_pntr(&len, ar, &st_ar);
  printf(" %d", ar[2]);
  if (success) {
    printf(" %d", -1);
  }
}

void print_all(int len_copy, int ar_copy[3], struct array_with_len st_ar_copy) {
  int i = 0;
  while (i < len_copy) {
    printf(" %d", ar_copy[i]);
    i = i + 1;
  }
  i = 0;
  while (i < st_ar_copy.len) {
    printf(" %d", st_ar_copy.ar[i]);
    i = i + 1;
  }
  ar_copy[2] = 42;
}

int print_all_pntr(int *len_ref, int *ar_ref, struct array_with_len *st_ar_ref) {
  int i = 0;
  ar_ref[2] = 3;
  while (i < *len_ref) {
    printf(" %d", ar_ref[i]);
    i = i + 1;
  }
  i = 0;
  while (i < (*st_ar_ref).len) {
    printf(" %d", (*st_ar_ref).ar[i]);
    i = i + 1;
  }
  return 1;
}

