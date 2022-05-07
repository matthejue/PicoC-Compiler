// in:32
// expected:42 42 42 42 42 1 0 1 0 42

void main() {
  // ------------------------- Arithmetic expressions -------------------------
  int var = input();
  print(var + 'n' - 100);
  print(-(-'*' + var * '\0'));
  print(-(' ' + -var) * '*' + '*');
  // ---------------------------- Logic expressions ---------------------------
  print((var * 2 == 'A' - 1) * 42);
  print(!0 * 42);
  int or_exp_true = 0 || var == 0 || !var + 1;
  int or_exp_false = 0 || 0 + !'A' || !var;
  int and_exp_true = 1 && !(var - var) && var != 0;
  int and_exp_false = 1 &&  var && !var;
  print(or_exp_true);
  print(or_exp_false);
  print(and_exp_true);
  print(and_exp_false);
  print((and_exp_true && and_exp_false + 1) + 41 * (or_exp_true || or_exp_false));
}
