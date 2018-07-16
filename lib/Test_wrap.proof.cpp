/**
 * @author  Tyler Robbins
 * @file    Test_wrap.proof.cpp
 * @date    2018-07-15 01:11:40
 */

#include "Test.h"

extern "C" {
    __declspec(dllexport) void* __pywrapped_Hello_Create() {
        return new Hello();
    }

    __declspec(dllexport) void* __pywrapped_Hello_Create_1(const char* p1) {
        return new Hello(std::string(p1));
    }

    __declspec(dllexport) void __pywrapped_Hello_Destroy(void* p1) {
        delete (Hello*)p1;
    }

    __declspec(dllexport) const char* __pywrapped_Hello_say(const void* p1) {
        const std::string& value = ((const Hello*)p1)->say();

        return value.c_str();
    }

    __declspec(dllexport) void __pywrapped_Hello_mparam(void* p1, int p2, float p3) {
        ((Hello*)p1)->mparam(p2, p3);
    }

    __declspec(dllexport) void __pywrapped_Hello_fparam(void* p1, int (*p2)(float)) {
        ((Hello*)p1)->fparam(std::function<int(float)>(p2));
    }
}
