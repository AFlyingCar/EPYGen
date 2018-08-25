#ifndef LITERAL_H
#define LITERAL_H

#include <string>

#include "Section.h"

namespace EpyGen {
    class PyLiteral: public Section {
        public:
            PyLiteral(const std::string&);

            const std::string& getLiteral() const;
            void setLiteral(const std::string&);

        private:
            std::string m_literal;
    };

    class CppLiteral: public Section {
        public:
            CppLiteral(const std::string&);

            const std::string& getLiteral() const;
            void setLiteral(const std::string&);

        private:
            std::string m_literal;
    };
}

#endif

