#include "Type.h"

#include <iostream>

#include "Util.h"

EpyGen::Type* parseType(const std::string& type_str, size_t& idx,
                        int sub = 0, int function = 0)
{
    // initialize c and p_c to \0 so that we have _something_ in there
    char c = '\0';
    // char p_c = '\0';
    std::string prev_token = "";
    std::string token = "";
    std::vector<std::string> namespaces;
    std::vector<EpyGen::Type*> tparams;
    std::vector<EpyGen::Type*> fparams;
    bool is_const = false;
    bool is_ptr = false;
    bool is_const_ptr = false;
    bool is_function = false;
    std::string t = "";

    while(idx < type_str.size()) {
        c = type_str[idx];

        if(c == ' ' || c == '\n' || c == '\t' || c == '\r') {
            prev_token = token;
            if(token == "const") {
                is_const = true;
                token = "";
            }
        } else if(c == '*') {
            if(prev_token == "const") {
                is_const_ptr = true;
                is_ptr = true;
            } else {
                is_ptr = true;
            }
        } else if(c == '&') {
            is_const_ptr = true;
            is_ptr = true;
        } else if(c == ':') {
            namespaces.push_back(EpyGen::Util::strip(token));
            token = "";
            ++idx;
            if(type_str[idx] != ':') {
                std::cerr << "ERROR: Need two `:`" << std::endl;
                return nullptr;
            }
        } else if(c == '<') {
            if(t.empty()) // Set t to be token if it has not already been set
                t = token;
            token = "";
            ++idx;
            EpyGen::Type* tp = parseType(type_str, idx, sub + 1, function);
            if(tp != nullptr)
                tparams.push_back(tp);
            while(type_str[idx] == ',') {
                ++idx;
                tp = parseType(type_str, idx, sub + 1, function);
                if(tp) tparams.push_back(tp);
            }
        } else if(c == '>') {
            if(sub > 0) {
                break;
            } else {
                std::cerr << "ERROR: mismatched <>";
                return nullptr;
            }
        } else if(c == '(') {
            if(t.empty()) // Set t to be token if it has not already been set
                t = token;
            token = "";
            ++idx;
            EpyGen::Type* f = parseType(type_str, idx, sub, function + 1);
            if(f != nullptr)
                fparams.push_back(f);
            while(type_str[idx] == ',') {
                ++idx;
                f = parseType(type_str, idx, sub, function + 1);
                if(f != nullptr)
                    fparams.push_back(f);
            }
            is_function = true;
        } else if(c == ')') {
            if(function > 0)
                break;
            else
                std::cout << "ERROR: mismatched ()" << std::endl;
            break;
        } else if(c == ',') {
            break;
        } else {
            token += c;
        }

        // p_c = c;
        ++idx;
    }

    // If the token is left all by itself, let's just pretend it was the type name,
    //  as there are no other valid possibilities for it to be
    if(!token.empty())
        t = EpyGen::Util::strip(token);

    if(!t.empty())
        return new EpyGen::Type{type_str, is_const, namespaces,
                                EpyGen::Util::strip(t), tparams, fparams,
                                is_ptr, is_const_ptr, is_function};
    else
        return nullptr;
}
EpyGen::Type::Type(const std::string&, bool, const std::vector<std::string>&,
                   const std::string&, const std::vector<Type*>&,
                   const std::vector<Type*>&, bool, bool, bool)
{
}

EpyGen::Type* EpyGen::Type::parseType(const std::string& type_str) {
    size_t idx = 0;
    return ::parseType(type_str, idx, 0, 0);
}

