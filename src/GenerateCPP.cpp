#include "GenerateCPP.h"

#include <map>
#include <string>

#include "Namespace.h"
#include "Class.h"
#include "Function.h"

std::string EpyGen::createCPPFunction(const std::string& full_name,
                                      const std::string& func_name,
                                      const Function* func,
                                      const Epy& epy,
                                      ThrowsList& ref_throws,
                                      bool in_class, size_t ident)
{
    (void)full_name;
    (void)func_name;
    (void)func;
    (void)epy;
    (void)ref_throws;
    (void)in_class;
    (void)ident;

    return "";
}

std::string EpyGen::createCPPClass(const Class* klass, const Epy& epy,
                                   ThrowsList& ref_throws)
{
    (void)klass;
    (void)epy;
    (void)ref_throws;
    return "";
}

std::string EpyGen::createCPPNamespace(const Namespace* nspace, const Epy& epy,
                                       ThrowsList& ref_throws)
{
    std::string nspace_string = "";

    std::string name = nspace->getName();
    size_t ident = 1;

    nspace_string += "extern \"C\" {\n";

    std::map<std::string, int> functions_found;
    for(const auto& f : nspace->getFunctions()) {
        if(!functions_found.count(f->name)) functions_found[f->name] = 0;

        std::string full_name = nspace->getFmtName() + '_' + f->name +
                                std::to_string(functions_found[f->name]);
        nspace_string += createCPPFunction(full_name, f->name, f, epy,
                                           ref_throws, false, ident);
    }

    nspace_string += "}";

    return nspace_string;
}

