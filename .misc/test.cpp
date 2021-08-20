#include <stdio.h>

void while_true() {
  do
    printf("\n");
  while (true);
}

int main(int argc, const char **argv) { while_true(); }
