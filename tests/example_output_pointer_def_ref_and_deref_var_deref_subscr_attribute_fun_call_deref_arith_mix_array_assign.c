// in:42 3
// expected:42 3 3 3 3 3 42

int *return_pntr(int **pntr);

struct array_with_len {int *ar; int len;};

void main() {
  // pointer definition
  int *pntr_on_int;  // pointer on integers
  int **pntr_on_pntr;  // pointer on pointers
  // reference and dereference operator on variable
  int var = input();
  pntr_on_int = &var;
  print(*pntr_on_int);
  // reference operator on a dereference operation
  int ar[3] = {4, 2, input()};
  pntr_on_int = &*(ar + 1 + 1);
  print(*pntr_on_int);
  // reference operator on a subscript operation
  pntr_on_int = &ar[1 + 1];
  print(*pntr_on_int);
  // reference operator on a attribute operation
  struct array_with_len st_ar = {.ar=ar, .len=3};
  pntr_on_pntr = &st_ar.ar;
  print(*(*pntr_on_pntr + st_ar.len - 1));
  // reference operator on return value of function call
  print(*(return_pntr(pntr_on_pntr) + st_ar.len - 1));
  // pointer mixed with array
  print(*(pntr_on_pntr[0] + 2));
  // assignment to deref
  *pntr_on_int = var;
  print(ar[2]);
}

int *return_pntr(int **pntr)
{
  return *pntr;
}
