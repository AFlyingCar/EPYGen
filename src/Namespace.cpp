
#include "Namespace.h"

EpyGen::Namespace::Namespace(const std::string& name): Section(name),
                                                       m_functions()
{ }

std::vector<EpyGen::Function*>& EpyGen::Namespace::getFunctions() {
    return m_functions;
}

void EpyGen::Namespace::addFunction(Function* func) {
    m_functions.push_back(func);
}

