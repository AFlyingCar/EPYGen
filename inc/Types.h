#ifndef TYPES_H
#define TYPES_H

#include <vector>
#include <tuple>

namespace EpyGen {
    class Section;
    class Type;

    using SectionList = std::vector<Section*>;
    using ParameterList = std::vector<std::tuple<Type*, bool>>;
    using ThrowsList = std::vector<std::string>;

    using EnumValue = std::tuple<std::string, std::string>;
}

#endif

