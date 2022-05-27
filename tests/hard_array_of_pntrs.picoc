// in:42
// expected:42 42 42 42 42 42

void main() {
  int var = input();
  int ar[3] = {1, var, 3};
  // array of pointers
  int *ar_of_pntrs[3];
  ar_of_pntrs[0] = ar;
  ar_of_pntrs[1] = &ar;
  ar_of_pntrs[2] = &var;
  print(ar_of_pntrs[0][1]);
  // the subtype of the array decides how the 2nd subscript behaves:
  print(ar_of_pntrs[1][1]);
  print(ar_of_pntrs[2][0]);
  print(*(*ar_of_pntrs + 1));
  print(*(*(ar_of_pntrs + 1) + 1));
  print(**(ar_of_pntrs + 2));
}
