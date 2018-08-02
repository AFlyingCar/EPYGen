/**
 * @author  Tyler Robbins
 * @file    Test.cpp
 * @date    2018-07-13 08:43:08
 */

#include "Test.h"

#include <iostream>

Hello::Hello(const std::string& m): m_message(m) { }
Hello::~Hello(){ }

std::string Hello::say() const {
    return m_message;
}

void Hello::mparam(int, float) {
    
}
void Hello::fparam(std::function<int(float, double)> f) {
    f(5, 4);
}


void Hello::sayHello() {
    std::cout << "Hello there!" << std::endl;
}

void Hello::throwTest() {
    throw 25;
}

