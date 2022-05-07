// in:42
// expected:42 42

void main() {
  // pointer on integers
  int *pntr_on_int;
  // pointer on arrays of size 2
  int (*pntr_on_array)[3];

  // --------------------------- pointer arithmetic ---------------------------
  int ar[3] = {1, input(), 3};

  // pointer on integers
  pntr_on_int = &*ar;
  // same as just 'ar' as 'ar' has the datatype 'array of int' = 'pointer of
  // int' in the symbol table, the value is the address of the first element
  print(*(pntr_on_int + 1));

  // pointer on arrays of size 2
  pntr_on_array = &ar;
  print(*(*pntr_on_array + 1));
}
