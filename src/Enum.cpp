
#include "Enum.h"

EpyGen::Enum::Enum(const std::string& name, bool eclass):
    Section(name),
    m_is_enum_class(eclass),
    m_values()
{ }

bool EpyGen::Enum::isEnumClass() const {
    return m_is_enum_class;
}

std::vector<std::tuple<std::string, std::string>>& EpyGen::Enum::getValues() {
    return m_values;
}

