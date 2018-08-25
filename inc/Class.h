#ifndef CLASS_H
#define CLASS_H

#include <vector>
#include <tuple>
#include <string>

#include "Namespace.h"
#include "Type.h"
#include "Types.h"

namespace EpyGen {
    struct CTor;
    class Class: public Namespace {
        public:
            Class(const std::string&, const ParameterList&);

            ParameterList& getTParams();

            const std::vector<CTor>& getCTors() const;
            void addCTor(const CTor&);

            const std::vector<Function*>& getVirtualFuncs() const;
            void addVirtualFunc(Function*);

            bool isAbstract() const;
            void setIsAbstract(bool);

            bool hasDTor() const;
            void setHasDTor(bool);

        private:
            ParameterList m_tparams;

            // Tuple: (param_list, tparam_list, throws, Class)
            std::vector<CTor> m_ctors;
            std::vector<Function*> m_virtual_funcs;
            bool m_abstract;

            // Nothing special needs to be done with the destructor, we just need to know that we have one
            bool m_dtor;
    };

    struct CTor {
        ParameterList m_param_list;
        ParameterList m_tparam_list;
        ThrowsList m_throws;
        Class* m_klass;
    };
}

#endif

