#include "Class.h"

EpyGen::Class::Class(const std::string& name, const ParameterList& tp_list):
    Namespace(name),
    m_tparams(tp_list),
    m_ctors(),
    m_virtual_funcs(),
    m_abstract(false),
    m_dtor(false)
{
}

EpyGen::ParameterList& EpyGen::Class::getTParams() {
    return m_tparams;
}

const std::vector<EpyGen::CTor>& EpyGen::Class::getCTors() const {
    return m_ctors;
}
void EpyGen::Class::addCTor(const CTor& ctor) {
    m_ctors.push_back(ctor);
}

const std::vector<EpyGen::Function*>& EpyGen::Class::getVirtualFuncs() const {
    return m_virtual_funcs;
}

void EpyGen::Class::addVirtualFunc(Function* func) {
    m_virtual_funcs.push_back(func);
}

bool EpyGen::Class::isAbstract() const {
    return m_abstract;
}

void EpyGen::Class::setIsAbstract(bool abstract) {
    m_abstract = abstract;
}

bool EpyGen::Class::hasDTor() const {
    return m_dtor;
}

void EpyGen::Class::setHasDTor(bool dtor) {
    m_dtor = dtor;
}


