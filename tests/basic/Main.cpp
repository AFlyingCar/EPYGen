
#include <iostream>

#include "Python.h"

#include "lib/Test.h"

int main() {
    std::cout << "Hello, World!" << std::endl;

    Py_Initialize();

    PyRun_SimpleString("import sys,os; sys.path.append(os.getcwd()); import a");

    Py_Finalize();

    return 0;
}
