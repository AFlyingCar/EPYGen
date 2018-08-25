
#include "Literal.h"

EpyGen::PyLiteral::PyLiteral(const std::string& name): Section(name),
                                                       m_literal()
{
}

const std::string& EpyGen::PyLiteral::getLiteral() const {
    return m_literal;
}

void EpyGen::PyLiteral::setLiteral(const std::string& literal) {
    m_literal = literal;
}

EpyGen::CppLiteral::CppLiteral(const std::string& name): Section(name),
                                                         m_literal()
{
}


const std::string& EpyGen::CppLiteral::getLiteral() const {
    return m_literal;
}

void EpyGen::CppLiteral::setLiteral(const std::string& literal) {
    m_literal = literal;
}

