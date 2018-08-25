#include "Util.h"

#include <algorithm>
#include <iterator>

std::vector<std::string> EpyGen::Util::split(const std::string& str, char delim) {
    std::vector<std::string> vec;

    split(str, delim, std::back_inserter(vec));

    return vec;
}

std::string& EpyGen::Util::lstrip_ip(std::string& s) {
    s.erase(s.begin(), std::find_if(s.begin(), s.end(),
            [](int c) { return !std::isspace(c); }));
    return s;
}

std::string& EpyGen::Util::rstrip_ip(std::string& s) {
    s.erase(std::find_if(s.rbegin(), s.rend(),
            [](int c) { return !std::isspace(c); }).base(), s.end());
    return s;
}

std::string& EpyGen::Util::strip_ip(std::string& s) { 
    rstrip(s);
    lstrip(s);
    return s;
}

std::string EpyGen::Util::lstrip(std::string s) {
    lstrip_ip(s);
    return s;
}

std::string EpyGen::Util::rstrip(std::string s) {
    rstrip_ip(s);
    return s;
}

std::string EpyGen::Util::strip(std::string s) { 
    return strip_ip(s);
}

bool EpyGen::Util::startswith(const std::string& str, const std::string& prefix) {
    return str.compare(0, prefix.size(), prefix) == 0;
}

bool EpyGen::Util::endswith(const std::string& str, const std::string& suffix) {
    return str.compare(str.size() - suffix.size(), suffix.size(), suffix) == 0;
}

