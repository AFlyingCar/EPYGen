#include "Generate.h"

#include <string>
#include <map>

#include "Constants.h"
#include "Types.h"
#include "Epy.h"
#include "Class.h"
#include "Namespace.h"
#include "Literal.h"
#include "GenerateCPP.h"

std::string EpyGen::generateCPP(const Epy& epy) {
    std::string cplusplus = EpyGen::CPP_HEADER; // .format(Constants.VERSION, Constants.TODAY)

    ThrowsList reffed_throws;

    for(const Section* sec : epy.getSections()) {
        auto klass_sec = dynamic_cast<const Class*>(sec);
        auto nspace_sec = dynamic_cast<const Namespace*>(sec);
        auto cppliteral_sec = dynamic_cast<const CppLiteral*>(sec);

        if(klass_sec != nullptr)
            cplusplus += createCPPClass(klass_sec, epy, reffed_throws);
        else if(nspace_sec != nullptr)
            cplusplus += createCPPNamespace(nspace_sec, epy, reffed_throws);
        else if(cppliteral_sec != nullptr)
            cplusplus += cppliteral_sec->getLiteral();
    }

    return cplusplus;
}

std::string EpyGen::generatePython(const Epy&) {
    return "";
}

