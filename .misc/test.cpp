#include <stdio.h>

void while_true() {
  if (true) {
    if (true) {
      printf("test");
    }
  } else if (true) {
    printf("test");
  } else {
    printf("test");
  }
}

int main(int argc, const char **argv) { while_true(); }
