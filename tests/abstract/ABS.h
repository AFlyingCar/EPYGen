#ifndef ABS_H
#define ABS_H

#include <string>

#include "API.h"

class API ABS {
    public:
        ABS();
        virtual ~ABS();

        virtual void pure(const std::string&) = 0;

        static void sayHelloThere();
        void sayGK();
};

#endif

