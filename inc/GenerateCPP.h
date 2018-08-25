#ifndef GENERATECPP_H
#define GENERATECPP_H

#include <string>

#include "Types.h"

namespace EpyGen {
    struct Function;
    class Epy;
    class Section;
    class Class;
    class Namespace;

    std::string createCPPFunction(const std::string&, const std::string&,
                                  const Function*, const Epy&, ThrowsList&, bool,
                                  size_t);

    std::string createCPPClass(const Class*, const Epy&, ThrowsList&);
    std::string createCPPNamespace(const Namespace*, const Epy&, ThrowsList&);
}

#endif

