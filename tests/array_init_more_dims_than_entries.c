// in:42
// expected:1 0 0 0 0 0 5 2 42 3 0 0 0 5 3 0 0 0 0 0 5 42
#include<stdio.h>

void main(){
    int ar[4][3][2] = {{1}, {2, 42, 3}, 3};
    printf(" %d", ar[0][0][0]);
    printf(" %d", ar[0][0][1]);
    printf(" %d", ar[0][1][0]);
    printf(" %d", ar[0][1][1]);
    printf(" %d", ar[0][2][0]);
    printf(" %d", ar[0][2][1]);

    printf(" %d", 5);

    printf(" %d", ar[1][0][0]);
    printf(" %d", ar[1][0][1]);
    printf(" %d", ar[1][1][0]);
    printf(" %d", ar[1][1][1]);
    printf(" %d", ar[1][2][0]);
    printf(" %d", ar[1][2][1]);

    printf(" %d", 5);

    printf(" %d", ar[2][0][0]);
    printf(" %d", ar[2][0][1]);
    printf(" %d", ar[2][1][0]);
    printf(" %d", ar[2][1][1]);
    printf(" %d", ar[2][2][0]);
    printf(" %d", ar[2][2][1]);

    printf(" %d", 5);

    printf(" %d", *(ar[1][0]+3-2));
}

