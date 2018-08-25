
#include "Epy.h"

#include <algorithm>
#include <iostream>
#include <tuple>

#include "Util.h"
#include "Section.h"
#include "Enum.h"
#include "Class.h"
#include "Type.h"
#include "Function.h"
#include "Literal.h"
#include "Types.h"

#define ENABLE_DEBUG true

std::string formatLibName(const std::string& lib_name) {
    // libfile.so.1 -> LIBFILE_SO_1

    std::string fmt_lib_name(lib_name);
    size_t start = 0;
    while((start = fmt_lib_name.find('.', start)) != std::string::npos) {
        fmt_lib_name.replace(start, 1, "_");
        start++;
    }
    start = 0;
    while((start = fmt_lib_name.find('/', start)) != std::string::npos) {
        fmt_lib_name.replace(start, 1, "_");
        start++;
    }
    start = 0;
    while((start = fmt_lib_name.find('\\', start)) != std::string::npos) {
        fmt_lib_name.replace(start, 1, "_");
        start++;
    }
    std::transform(fmt_lib_name.begin(), fmt_lib_name.end(), fmt_lib_name.begin(),
                   [](char c) { return std::toupper(c); });

    return fmt_lib_name;
}

EpyGen::Epy::Epy(const std::string& filename, const std::string& contents,
                 const std::string& lib_name):
    m_filename(filename),
    m_library(lib_name),
    m_library_formatted(formatLibName(lib_name)),
    m_module_name(),
    m_sections(),
    m_has_classes(false),
    m_has_enums(false),
    m_has_namespaces(false)
{
    parse(contents);
}

const std::string& EpyGen::Epy::getFilename() const {
    return m_filename;
}

const std::string& EpyGen::Epy::getLibrary() const {
    return m_library;
}

const std::string& EpyGen::Epy::getFmtLibrary() const {
    return m_library_formatted;
}

const std::string& EpyGen::Epy::getModuleName() const {
    return m_module_name;
}

const std::vector<EpyGen::Section*>& EpyGen::Epy::getSections() const {
    return m_sections;
}

bool EpyGen::Epy::hasClasses() const {
    return m_has_classes;
}
bool EpyGen::Epy::hasEnums() const {
    return m_has_enums;
}
bool EpyGen::Epy::hasNamespaces() const {
    return m_has_namespaces;
}

void EpyGen::Epy::parse(const std::string& contents) {
    State state;
    std::string statement;

    for(size_t i = 0; i < contents.size(); ++i) {
        char c = contents[i];

        if(c == ';' && !(state.in_literalpy || state.in_literalcpp)) {
            parseStatement(Util::strip(statement), state);
            statement = "";
        } else if(c == '@') {
            ++i;
            std::string ppstatement = "";

            // Ignore non-linebreaking whitespace
            while(i < contents.size() && (contents[i] == ' ' ||
                                          contents[i] == '\t'))
                ++i;
            while(i < contents.size() && !(contents[i] == ' '  ||
                                           contents[i] == '\n' ||
                                           contents[i] == '\r' ||
                                           contents[i] == '\t'))
            {
                ppstatement += contents[i];
                ++i;
            }

            if(ppstatement.empty()) {
                if(state.in_literalpy) {
                    state.in_literalpy = false;
                    m_sections.push_back(new PyLiteral(statement));

                    statement = "";
                } else if(state.in_literalcpp) {
                    state.in_literalcpp = false;
                    m_sections.push_back(new CppLiteral(statement));

                    statement = "";
                } else {
                    std::cerr << "Error: Encountered closing @ when outside of "
                              << "literal block." << std::endl;
                }
            } else if(ppstatement == "py") {
                state.in_literalpy = true;
            } else if(ppstatement == "cpp") {
                state.in_literalcpp = true;
            } else if(ppstatement == "include") {
                // TODO
            } else {
                std::cerr << "Unrecognized ppstatement `" << ppstatement << "`"
                          << std::endl;
                return;
            }
        } else {
            if(c == '/' && !(state.in_literalpy || state.in_literalcpp)) {
                ++i;
                if(contents[i] == '/') {
                    while(i < contents.size() && contents[i] != '\n') ++i;
                    continue;
                }  else if(contents[i] == '*') {
                    size_t j = i - 1;

                    while(i < contents.size() && !(contents[j] == '*' &&
                                                   contents[i] == '/'))
                    {
                        ++i;
                        ++j;
                    }

                    ++i; // Increment one more time to get past that pesky closing /
                    continue;
                }

            }
            statement += c;
            state.prev_c = c;
        }
    }
}

void EpyGen::Epy::parseStatement(const std::string& statement, State& state) {
    if(ENABLE_DEBUG)
        std::cout << "Statement: " << statement << std::endl;

    if(!state.in_section && m_module_name.empty()) {
        m_module_name = statement;
    } else if(statement == "start") {
        state.in_section = true;
    } else if(statement == "end") {
        state.in_section = false;
        if(state.sobj) {
            m_sections.push_back(state.sobj);
        } else {
            std::cerr << "Internal Error: sobj is NULL" << std::endl;
            state.error = true;
            return;
        }
    } else if(Util::startswith(statement, "class")) {
        parseClassStatement(statement, state);
        m_has_classes = true;
    } else if(Util::startswith(statement, "namespace")) {
        parseNamespaceStatement(statement, state);
    } else if(Util::startswith(statement, "enum")) {
        parseEnumStatement(statement, state);
        m_has_enums = true;
    } else if(Util::startswith(statement, "ctor")) {
        if(state.sobj == nullptr) {
            std::cerr << "Internal Error: sobj is NULL" << std::endl;
            state.error = true;
        }
        parseCtorStatement(statement, state);
    } else if(Util::startswith(statement, "dtor")) {
        if(state.sobj == nullptr) {
            std::cerr << "Internal Error: sobj is NULL" << std::endl;
            state.error = true;
        }
        parseDtorStatement(statement, state);
    } else if(Util::startswith(statement, "func")) {
        if(state.sobj == nullptr) {
            std::cerr << "Internal Error: sobj is None" << std::endl;
            state.error = true;
        }
        parseFunc(statement, state);
    } else if(Util::startswith(statement, "operator")) {
        if(state.sobj == nullptr) {
            std::cerr << "Internal Error: sobj is NULL." << std::endl;
            state.error = true;
        }
        parseOperator(statement, state);
    } else if(state.stype == Section::Type::ENUM_TYPE) {
        std::tuple<std::string, std::string> value = parseEnumValue(statement,
                                                                    state);

        if(state.sobj == nullptr) {
            std::cerr << "Internal Error: sobj is NULL" << std::endl;
            state.error = true;
        }

        Enum* sec_enum = dynamic_cast<Enum*>(state.sobj);

        if(sec_enum == nullptr) {
            std::cerr << "Internal Error: sobj is not Enum" << std::endl;
            state.error = true;
        }

        sec_enum->getValues().push_back(value);
    }
}

EpyGen::ParameterList EpyGen::Epy::parseTParams(const std::string& param_str_) {
    std::string param_str= Util::strip(param_str_); // Just to be safe

    ParameterList params;

    if(!(Util::startswith(param_str, "<") && Util::endswith(param_str, ">"))) {
        std::cerr << "Error: Template parameter lists must be surrounded with <>"
                  << std::endl;
        return params;
    }

    if(ENABLE_DEBUG)
        std::cout << "parsing tparam list" << std::endl;

    // Make sure we chop off the closing parenthesis
    param_str = param_str.substr(1, param_str.size() - 2);

    size_t pcount = 0;
    std::string ptype = "";
    bool defaulted = false;

    for(size_t i = 0; i < param_str.size(); ++i) {
        char c = param_str[i];

        if(c == ',' and pcount == 0) {
            if(ENABLE_DEBUG)
                std::cout << "Found parameter `" << ptype << "`" << std::endl;
            params.push_back(std::make_tuple(Type::parseType(Util::strip(ptype)),
                                             defaulted));
            ptype = "";
            defaulted = false;
            ++i; // skip over the comma
            continue;
        } else if(c == '=') {
            defaulted = true;
            ++i;
            continue;
        } else if(c == '<') { // Handle template parameters and function pointers
            ++pcount;
        } else if(c == '(') {
            ++pcount;
        } else if(c == '>') {
            --pcount;
        } else if( c == ')') {
            --pcount;
        }

        ptype += c;
    }

    if(!ptype.empty()) {
        if(ENABLE_DEBUG)
            std::cout << "Found parameter `" + ptype + "`" << std::endl;
        params.push_back(std::make_tuple(Type::parseType(Util::strip(ptype)),
                                         defaulted));
    }

    if(ENABLE_DEBUG) {
        std::cout << "Found " << params.size() << " template parameters"
                  << std::endl;
        std::cout << "done" << std::endl;
    }

    return params;
}

std::tuple<EpyGen::ParameterList, std::string> EpyGen::Epy::parseParamList(const std::string& param_str_)
{
    std::string param_str = Util::strip(param_str_); // Just to be safe

    std::string throws_str = Util::strip(param_str.substr(param_str.rfind(')') + 1));
    param_str = Util::strip(param_str.substr(0, param_str.rfind(')') + 1));

    if(!(Util::startswith(param_str, "(") and Util::endswith(param_str, ")"))) {
        std::cerr << "Error: Parameter lists must be surrounded with ()"
                  << std::endl;
        return std::make_tuple(ParameterList(), "\21");
    }

    if(ENABLE_DEBUG)
        std::cout << "parsing param list" << std::endl;

    // Chop off the closing parenthesis before we do anything else
    param_str = param_str.substr(1, param_str.size() - 2);

    ParameterList params;

    size_t pcount = 0;
    std::string ptype = "";
    bool defaulted = false;
    for(size_t i = 0; i < param_str.size(); ++i) {
        char c = param_str[i];

        if(c == ',' && pcount == 0) {
            if(ENABLE_DEBUG)
                std::cout << "Found parameter `" << ptype << "`" << std::endl;
            params.push_back(std::make_tuple(Type::parseType(Util::strip(ptype)),
                                             defaulted));
            ptype = "";
            defaulted = false;
            // ++i; // skip over the comma
            continue;
        } else if(c == '=') {
            defaulted = true;
            // ++i;
            continue;
        }

        // Handle template parameters and function pointers
        else if(c == '<') {
            pcount += 1;
        } else if(c == '(') {
            pcount += 1;
        } else if(c == '>') {
            pcount -= 1;
        } else if(c == ')') {
            pcount -= 1;
        }
        ptype += c;
    }

    if(!ptype.empty()) {
        if(ENABLE_DEBUG)
            std::cout << "Found parameter `" << ptype << "`" << std::endl;
        params.push_back(std::make_tuple(Type::parseType(Util::strip(ptype)),
                                         defaulted));
    }

    if(ENABLE_DEBUG) {
        std::cout << "Found " << params.size() << " parameters" << std::endl;
        std::cout << "done" << std::endl;
    }

    return std::make_tuple(params, throws_str);
}

EpyGen::ThrowsList EpyGen::Epy::parseThrowsStr(const std::string& throws_str_) {
    ThrowsList throws;
    std::string throws_str = Util::strip(throws_str_);
    if(Util::startswith(throws_str, "throws ")) {
        size_t last = 0;
        std::string wout_throws_kword = throws_str.substr(7);
        for(size_t i = 0; i < wout_throws_kword.size(); ++i) {
            if(wout_throws_kword[i] == ',') {
                throws.push_back(Util::strip(wout_throws_kword.substr(last, i)));
                last = i;
            }
        }
    }

    return throws;
}

void EpyGen::Epy::parseCtorStatement(const std::string& statement, State& state)
{
    Class* sobj = dynamic_cast<Class*>(state.sobj);
    if(sobj == nullptr) {
        std::cerr << "Internal Error: sobj is not a Class" << std::endl;
        state.error = true;
        return;
    }

    std::string rest = Util::lstrip(statement.substr(4));
    size_t paren_loc = rest.find('(');
    std::string tparam_str = Util::rstrip(rest.substr(0, paren_loc));
    std::string param_str = Util::lstrip(rest.substr(paren_loc));

    ParameterList tparam_list;

    // param_str = '(' + param_str.lstrip()
    size_t tparam_start_loc = tparam_str.find('<');
    if(tparam_start_loc != std::string::npos)
        tparam_list = parseTParams(tparam_str);

    auto res = parseParamList(param_str);
    ParameterList param_list = std::get<0>(res);
    std::string throws_str = std::get<1>(res);

    if(ENABLE_DEBUG)
        std::cout << throws_str << std::endl;

    std::vector<std::string> throws = parseThrowsStr(throws_str);

    if(throws_str[0] == '\21')
        state.error = true;
    else
        sobj->addCTor(CTor{param_list, tparam_list, throws, sobj});
}

void EpyGen::Epy::parseDtorStatement(const std::string&, State& state)
{
    Class* sobj = dynamic_cast<Class*>(state.sobj);
    if(sobj == nullptr) {
        std::cerr << "Internal Error: sobj is not Class";
        state.error = true;
        return;
    }

    sobj->setHasDTor(true);
}

void EpyGen::Epy::parseFunc(const std::string& statement, State& state) {
    bool isclass = false;

    Class* klass_sobj = dynamic_cast<Class*>(state.sobj);
    Namespace* nspace_sobj = dynamic_cast<Namespace*>(state.sobj);

    if(klass_sobj) {
        isclass = true;
    } else if(nspace_sobj) {
        isclass = false;
    } else {
        std::cerr << "Internal Error: sobj is not a Class or Namespace"
                  << std::endl;
        state.error = true;
        return;
    }

    std::string func = Util::lstrip(statement.substr(4));
    
    size_t ret_sep = func.find_last_of("->");
    // substring from 1 after ret_sep, since `->` is 2 chars
    std::string rtype = Util::lstrip(func.substr(ret_sep + 1));
    func = Util::rstrip(func.substr(0, ret_sep - 1));

    if(ENABLE_DEBUG)
        std::cout << "==> " << func << std::endl;

    bool is_const = false;
    bool is_static = false;
    bool is_virtual = false;
    bool is_abstract = false;

    // class specific parsing
    // We check the space after each one to make sure the keywords aren't part
    //  of the next token
    if(Util::startswith(func, "const ")) {
        if(!isclass) {
            std::cerr << "Error: const only allowed on class sections."
                      << std::endl;
            state.error = true;
            return;
        }
        is_const = true;
        func = Util::lstrip(func.substr(5));
    }
    if(Util::startswith(func, "static ")) {
        if(!isclass) {
            std::cerr << "Error: static only allowed on class sections."
                      << std::endl;
            state.error = true;
            return;
        }
        is_static = true;
        func = Util::lstrip(func.substr(6));
    } else if(Util::startswith(func, "virtual ")) {
        if(!isclass) {
            std::cerr << "Error: virtual only allowed on class sections."
                      << std::endl;
            state.error = true;
            return;
        }
        is_virtual = true;
        func = Util::lstrip(func.substr(8));
    } else if(Util::startswith(func, "abstract ")) {
        if(isclass) {
            std::cerr << "Error: abstract only allowed on class sections."
                      << std::endl;
            state.error = true;
            return;
        }
        is_virtual = true;
        is_abstract = true;
        func = Util::lstrip(func.substr(9));
    }

    size_t paren_loc = func.find('(');
    std::string func_and_tparams = func.substr(0, paren_loc);
    std::string param_str = Util::lstrip(func.substr(paren_loc));

    std::string tparams;
    size_t tparam_start_loc = func_and_tparams.find('<');
    if(tparam_start_loc != std::string::npos) {
        func = func_and_tparams.substr(0, tparam_start_loc);
        tparams = func_and_tparams.substr(tparam_start_loc);
    } else {
        func = func_and_tparams;
        tparams = "<>";
    }

    if(ENABLE_DEBUG)
        std::cout << "Parsing function `" << func << "` with rtype `" << rtype
                  << "`, parameters " << param_str << " tparams " << tparams
                  << " and modifiers " << (is_const ? "const " : "")
                  << (is_static ? "static " : "")
                  << (is_virtual ? "virtual" : "")
                  << (is_abstract ? "abstract" : "") << std::endl;

    auto res = parseParamList(param_str);
    ParameterList param_list = std::get<0>(res);
    std::string throws_str = std::get<1>(res);

    ParameterList tparam_list = parseTParams(tparams);

    ThrowsList throws = parseThrowsStr(throws_str);

    // Verify that there are no spaces in the function name
    for(const auto& c : func) {
        if(std::isspace(c)) {
            std::cerr << "Invalid function name `" << func << '`' << std::endl;
            state.error = true;
            return;
        }
    }

    Function* func_obj = new Function{func, Type::parseType(rtype), param_list,
                                      tparam_list, is_const, is_static,
                                      is_virtual, is_abstract, throws,
                                      nspace_sobj};

    // Generate Function object and append to sobj
    nspace_sobj->addFunction(func_obj);
    if(is_virtual) {
        klass_sobj->addVirtualFunc(func_obj);
    }
    if(is_abstract) {
        klass_sobj->setIsAbstract(true);
    }
}

void EpyGen::Epy::parseOperator(const std::string& statement, State& state) {
    bool isclass = false;

    Class* sobj = dynamic_cast<Class*>(state.sobj);
    if(sobj != nullptr) {
        isclass = true;
    } else {
        std::cerr << "Internal Error: sobj is  not Class" << std::endl;
        state.error = true;
        return;
    }

    std::string func = Util::lstrip(statement.substr(8));

    size_t ret_sep = func.find_last_of("->");
    std::string rtype = Util::lstrip(func.substr(ret_sep));
    func = Util::rstrip(func.substr(0, ret_sep));

    bool is_const = false;
    bool is_static = false;
    bool is_virtual = false;
    bool is_abstract = false;

    // class specific parsing
    // We check the space after each one to make sure the keywords aren't part
    //  of the next token
    if(Util::startswith(func, "const ")) {
        if(!isclass) {
            std::cerr << "Error: const only allowed on class sections."
                      << std::endl;
            state.error = true;
            return;
        }
        is_const = true;
        func = Util::lstrip(func.substr(5));
    }
    if(Util::startswith(func, "static ")) {
        if(!isclass) {
            std::cerr << "Error: static only allowed on class sections."
                      << std::endl;
            state.error = true;
            return;
        }
        is_static = true;
        func = Util::lstrip(func.substr(6));
    } else if(Util::startswith(func, "virtual ")) {
        if(!isclass) {
            std::cerr << "Error: virtual only allowed on class sections."
                      << std::endl;
            state.error = true;
            return;
        }
        is_virtual = true;
        func = Util::lstrip(func.substr(6));
    } else if(Util::startswith(func, "abstract ")) {
        if(!isclass) {
            std::cerr << "Error: abstract only allowed on class sections."
                      << std::endl;
            state.error = true;
            return;
        }
        is_virtual = true;
        is_abstract = true;
        func = Util::lstrip(func.substr(9));
    }

    size_t paren_loc = func.find('(');
    std::string func_and_tparams = func.substr(0, paren_loc);
    std::string param_str = func.substr(paren_loc);
    std::string tparams;

    size_t tparam_start_loc = func_and_tparams.find('<');
    if(tparam_start_loc != std::string::npos) {
        func = func_and_tparams.substr(0, tparam_start_loc);
        tparams = '<' + func_and_tparams.substr(tparam_start_loc);
    } else {
        func = func_and_tparams;
        tparams = "<>";
    }
    param_str = '(' + Util::lstrip(param_str);

    if(ENABLE_DEBUG)
        std::cout << "Parsing function `" << func << "` with rtype `" << rtype
                  << "`, parameters " << param_str << " tparams " << tparams
                  << "and modifiers" << (is_const ? "const " : "")
                  << (is_static ? "static " : "")
                  << (is_virtual ? "virtual" : "")
                  << (is_abstract ? "abstract" : "") << std::endl;

    auto res = parseParamList(param_str);
    ParameterList param_list = std::get<0>(res);
    std::string throws_str = std::get<1>(res);

    ParameterList tparam_list = parseTParams(tparams);

    std::vector<std::string> throws = parseThrowsStr(throws_str);

    // Verify that there are no spaces in the function name
    for(const auto& c : func) {
        if(std::isspace(c)) {
            std::cerr << "Invalid function name `" << func << '`' << std::endl;
            state.error = true;
            return;
        }
    }

    Operator* op = new Operator{{func, Type::parseType(rtype), param_list,
                                tparam_list, is_const, is_static, is_virtual,
                                is_abstract, throws, sobj}};

    // Generate Function object and append to sobj
    sobj->addFunction(op);
    if(is_virtual) {
        sobj->addVirtualFunc(op);
    }
    if(is_abstract) {
        sobj->setIsAbstract(true);
    }
}

void EpyGen::Epy::parseClassStatement(const std::string& statement,
                                      State& state)
{
    state.stype = Section::Type::CLASS_TYPE;

    // Parse name
    std::string left = Util::lstrip(statement.substr(5));
    size_t tstart = left.find("<");
    ParameterList tparams;
    if(tstart != std::string::npos) {
        tparams = parseTParams(left.substr(tstart));
        state.sname = left.substr(0, tstart);
    } else {
        state.sname = left;
    }

    state.sobj = new Class(state.sname, tparams);
}

void EpyGen::Epy::parseEnumStatement(const std::string&, State&) {
}

void EpyGen::Epy::parseNamespaceStatement(const std::string&, State&) {
}

EpyGen::EnumValue EpyGen::Epy::parseEnumValue(const std::string& statement,
                                              State& state)
{
    Section* sobj = dynamic_cast<Enum*>(state.sobj);
    if(sobj == nullptr) {
        std::cerr << "Internal Error: Values cannot be specified outside of"
                  << "enumerations." << std::endl;
        state.error = true;
        return std::make_tuple("","");
    }

    size_t value_assignment_loc = statement.find('=');

    std::string name;
    std::string default_value;

    if(value_assignment_loc != std::string::npos) {
        name = Util::rstrip(statement.substr(0, value_assignment_loc));
        default_value = Util::lstrip(statement.substr(value_assignment_loc));
    } else {
        name = statement;
        default_value = "";
    }

    return std::make_tuple(name, default_value);
}

