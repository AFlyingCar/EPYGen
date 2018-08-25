#ifndef SECTION_H
#define SECTION_H

#include <string>

namespace EpyGen {
    class Section {
        public:
            enum class Type {
                NAMESPACE_TYPE,
                CLASS_TYPE,
                ENUM_TYPE
            };

            Section(const std::string&);
            virtual ~Section();

            const std::string& getName() const;
            const std::string& getFmtName() const;

            virtual std::string str() const;

        private:
            std::string m_name;
            std::string m_fmt_name;
    };
}

#endif

