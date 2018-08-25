#include "Section.h"

namespace {
    std::string formatName(const std::string& name) {
        std::string s = name;
        for(size_t loc = s.find("::"); loc != std::string::npos;
            loc = s.find("::"))
        {
            s.replace(loc, 2, "_");
        }
        return std::string("_pywrapped_") + s;
    }
}

EpyGen::Section::Section(const std::string& name):
    m_name(name), 
    m_fmt_name(formatName(name))
{
}

EpyGen::Section::~Section() { }

const std::string& EpyGen::Section::getName() const {
    return m_name;
}

std::string EpyGen::Section::str() const {
    return m_name;
}

