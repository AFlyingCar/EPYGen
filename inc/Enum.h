#ifndef ENUM_H
#define ENUM_H

#include <vector>
#include <string>
#include <tuple>

#include "Section.h"

namespace EpyGen {
    class Enum: public Section {
        public:
            Enum(const std::string&, bool);

            bool isEnumClass() const;

            std::vector<std::tuple<std::string, std::string>>& getValues();
        private:
            bool m_is_enum_class;
            std::vector<std::tuple<std::string, std::string>> m_values;
    };
}

#endif

