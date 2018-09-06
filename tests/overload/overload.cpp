#include <iostream>

#include "overload.h"

int foo() {
    return 5;
}
void foo(int a, float b) {
    std::cout << a << " + " << b << " = " << a + b << std::endl;
}
float foo(int a, float b, int c, double d) {
    std::cout << "foo(" << a << "," << b << "," << c << "," << d << ")"
              << std::endl;
    return b;
}
int foo(std::function<int()> func) {
    std::cout << "foo(function_ptr)" << std::endl;
    return func();
}
