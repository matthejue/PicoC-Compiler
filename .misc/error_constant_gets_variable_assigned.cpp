#include <stdio.h>
#include <iostream>

int main(int argc, char *argv[]) {
  const char x = 'c';
  char car;
  std::cout  << "Enter your number: ";
  std::cin >> car;
  std::cout << car;
  int var = car;
  printf("%d\n", var);
  const char y = 'c';
  printf("%d\n", y);
  int tar = var + car;
  printf("%d\n", tar);
  const char z = 'c';
  printf("%d\n", z);
  return 0;
}
