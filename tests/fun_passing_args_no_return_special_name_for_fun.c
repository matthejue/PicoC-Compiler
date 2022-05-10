// in:21
// expected:42
#include<stdio.h>

void _fun120(char c, int i);

void main(){
  _fun120('b', 21);
}

void _fun120(char c, int i){
  printf(" %d", i * (100 + -c));
}

