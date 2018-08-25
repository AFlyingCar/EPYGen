#ifndef TYPE_H
#define TYPE_H

#include <string>
#include <vector>

namespace EpyGen {
    class Type {
        public:
            Type(const std::string&, bool, const std::vector<std::string>&,
                 const std::string&, const std::vector<Type*>&,
                 const std::vector<Type*>&, bool, bool, bool);
            static Type* parseType(const std::string&);
    };
}

#endif

