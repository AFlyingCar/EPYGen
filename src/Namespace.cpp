
#include "Namespace.h"

EpyGen::Namespace::Namespace(const std::string& name): Section(name),
                                                       m_functions()
{ }

const std::vector<EpyGen::Function*>& EpyGen::Namespace::getFunctions() const {
    return m_functions;
}

void EpyGen::Namespace::addFunction(Function* func) {
    m_functions.push_back(func);
}

