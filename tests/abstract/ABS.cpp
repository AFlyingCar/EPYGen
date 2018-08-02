
#include "ABS.h"

#include <iostream>

ABS::ABS() {
    std::cout << "Creating ABS" << std::endl;
}

ABS::~ABS() {
    std::cout << "Destroying ABS" << std::endl;
}

void ABS::sayHelloThere() {
    std::cout << "Hello there." << std::endl;
}

void ABS::sayGK() {
    std::cout << "General Kenobi!" << std::endl;
}
