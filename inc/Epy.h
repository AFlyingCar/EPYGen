#ifndef EPY_H
#define EPY_H

#include <string>
#include <vector>

#include "Section.h"
#include "Types.h"

namespace EpyGen {
    class Type;
    /**
     * @brief Represents a single Epy file
     */
    class Epy final {
        struct State {
            bool in_literalpy = false;
            bool in_literalcpp = false;
            bool in_section = false;
            bool error = false;
            std::string sname = "";
            Section* sobj = nullptr;
            std::string prev_c = "";
            Section::Type stype;
        };

        public:
            Epy(const std::string&, const std::string&, const std::string&);

            const std::string& getFilename() const;
            const std::string& getLibrary() const;
            const std::string& getFmtLibrary() const;

            const std::string& getModuleName() const;

            const SectionList& getSections() const;

            bool hasClasses() const;
            bool hasEnums() const;
            bool hasNamespaces() const;

        private:
            void parse(const std::string&);
            ParameterList parseTParams(const std::string&);
            std::tuple<ParameterList, std::string> parseParamList(const std::string&);
            ThrowsList parseThrowsStr(const std::string&);
            void parseCtorStatement(const std::string&, State&);
            void parseDtorStatement(const std::string&, State&);
            void parseFunc(const std::string&, State&);
            void parseOperator(const std::string&, State&);
            void parseStatement(const std::string&, State&);
            void parseClassStatement(const std::string&, State&);
            void parseEnumStatement(const std::string&, State&);
            void parseNamespaceStatement(const std::string&, State&);
            std::tuple<std::string, std::string> parseEnumValue(const std::string&,
                                                                State&);

            std::string m_filename;
            std::string m_library;
            std::string m_library_formatted;

            std::string m_module_name;
            SectionList m_sections;

            bool m_has_classes;
            bool m_has_enums;
            bool m_has_namespaces;
    };
}

#endif

