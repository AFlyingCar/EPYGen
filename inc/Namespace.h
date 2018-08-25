#ifndef NAMESPACE_H
#define NAMESPACE_H

#include <vector>

#include "Section.h"
#include "Function.h"

namespace EpyGen {
    class Namespace: public Section {
        public:
            Namespace(const std::string&);

            const std::vector<Function*>& getFunctions() const;
            void addFunction(Function*);

        private:
            std::vector<Function*> m_functions;
    };
}

#endif

