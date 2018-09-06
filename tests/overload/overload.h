#include "API.h"
#include <functional>

API int foo();
API void foo(int, float);
API float foo(int, float, int, double);
API int foo(std::function<int()>);
