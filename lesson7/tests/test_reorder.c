#include <stdio.h>

int test_commutative(int n) {
    // operands should get swapped
    int a = n + 42;
    int b = n * 31;
    int c = n | 7;
    int d = n & 1;

    // operands should not get swapped
    int e = 13 + n;
    int f = n - 10;

    return a + b + c + d + e + f;
}

int main() {
    // results should be the same with or without reordering pass
    printf("result for input=0: %d\n", test_commutative(0));
    printf("result for input=5: %d\n", test_commutative(5));
    printf("result for input=99: %d\n", test_commutative(99));
    return 0;
}
