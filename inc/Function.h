
#ifndef FUNCTION_H
#define FUNCTION_H

#include <string>
#include <vector>
#include <tuple>

#include "Type.h"
#include "Types.h"

namespace EpyGen {
    class Namespace;

    struct Function {
        std::string name;
        Type* rtype;
        ParameterList param_list;
        ParameterList tparam_list;
        bool is_const;
        bool is_static;
        bool is_virtual;
        bool is_abstract;
        ThrowsList throws;
        Namespace* owner;
    };

    struct Operator: public Function { };
}

#endif

