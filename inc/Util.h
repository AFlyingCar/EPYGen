#ifndef UTIL_H
#define UTIL_H

#include <sstream>
#include <vector>
#include <string>

namespace EpyGen {
    namespace Util {
        template<typename Iter>
        std::string join(Iter begin, Iter end, const std::string& glue) {
            std::stringstream stream;
            while(begin != end) {
                stream << *begin;
                ++begin;

                // Make sure we don't add glue at the end
                if(begin != end)
                    stream << glue;
            }

            return stream.str();
        }

        template<typename Out>
        void split(const std::string& str, char delim, Out result) {
            std::stringstream stream(str);
            std::string item;

            while(std::getline(stream, item, delim)) {
                (*result++) = item;
            }
        }

        std::string& lstrip_ip(std::string&);
        std::string& rstrip_ip(std::string&);
        std::string& strip_ip(std::string&);

        std::string lstrip(std::string);
        std::string rstrip(std::string);
        std::string strip(std::string);

        std::vector<std::string> split(const std::string&, char);

        bool startswith(const std::string&, const std::string&);
        bool endswith(const std::string&, const std::string&);
    }
}

#endif

