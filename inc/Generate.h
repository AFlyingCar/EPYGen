#ifndef GENERATE_H
#define GENERATE_H

#include <string>

namespace EpyGen {
    class Epy;

    std::string generateCPP(const Epy&);
    std::string generatePython(const Epy&);
}

#endif

