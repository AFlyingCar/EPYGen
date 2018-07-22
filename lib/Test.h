#ifndef TEST_H
#define TEST_H

#include <string>
#include <functional>

#include "API.h"

class API Hello {
    public:
        Hello(const std::string& = "Hello, World!");
        ~Hello();

        const std::string& say() const;

        void mparam(int, float);

        void fparam(std::function<int(float, double)>);

        static void sayHello();

    private:
        std::string m_message;
};

#endif
