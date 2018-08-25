#include <iostream>
#include <string>
#include <vector>
#include <fstream>
#include <sstream>

#include "Epy.h"
#include "Util.h"
#include "Generate.h"

#ifndef ENABLE_DEBUG
#define ENABLE_DEBUG true
#endif

void help() {
    std::cout << "EpyGen LIB_NAME [OPTIONS...] FILES...\n" << std::endl;

    std::cout << "Options:" << std::endl;
    std::cout << "    -h,--help    Displays this message and exits." << std::endl;
    std::cout << "    -d,--debug   Enables debug printing." << std::endl;
}

int parse(const std::string& filename, const std::string& lib_obj_name,
          std::vector<EpyGen::Epy>& epys)
{
    std::ifstream file(filename);
    if(!file) {
        std::cerr << "ERROR: Failed to open file `" << filename << std::endl;
        return 1;
    }
    std::stringstream contents;
    contents << file.rdbuf();

    std::string lib_obj_name_fixed = lib_obj_name;
    for(size_t loc = lib_obj_name_fixed.find('\\'); loc != std::string::npos;
        loc = lib_obj_name_fixed.find('\\'))
    {
        lib_obj_name_fixed.replace(loc, 1, "\\\\");
    }

    // Parse the Epy file
    epys.push_back(EpyGen::Epy(filename, EpyGen::Util::strip(contents.str()),
                               lib_obj_name_fixed));
    return 0;
}

int generate(const EpyGen::Epy& epy) {
    const std::string& filename = epy.getFilename();

    if(ENABLE_DEBUG) {
        std::cout << "EPY\n===" << std::endl;
        std::cout << "filename: " << filename << std::endl;
        std::cout << "has class: " << epy.hasClasses() << std::endl;
        std::cout << "has enum: " << epy.hasEnums() << std::endl;

        for(auto& section: epy.getSections())
            std::cout << section->str() << std::endl;
    }

    // Generate all Python code
    std::string python = EpyGen::generatePython(epy);

    if(ENABLE_DEBUG) {
        std::cout << "PYTHON\n======\n" << std::endl;
        std::cout << python << std::endl;
    }

    // Generate all C++ code
    std::string cpp = EpyGen::generateCPP(epy);

    if(ENABLE_DEBUG) {
        std::cout << "CPP\n===\n" << std::endl;
        std::cout << cpp << std::endl;
    }

    // Determine where the python and C++ files will be written to.
    std::string py_name = filename.substr(0, filename.size() - 3) + "py";
    std::string cpp_name = filename.substr(0, filename.size() - 4) + "_wrap.cpp";

    // Write them!
    if(ENABLE_DEBUG) {
        std::cout << "Writing to " << py_name << std::endl;
    }
    // TODO: Write PYTHON
    // open(py_name, 'w').write(python)

    if(ENABLE_DEBUG) {
        std::cout << "Writing to " << cpp_name << std::endl;
    }
    // TODO: Write C++
    // open(cpp_name, 'w').write(cpp)

    return 0;
}

int main(int argc, char** argv) {
    if(argc < 2) {
        std::cerr << "Invalid number of arguments." << std::endl;
        return 1;
    }

    std::string lib_obj_name = argv[1];
    std::vector<std::string> filenames;
    std::vector<EpyGen::Epy> epy_list;

    int i = argv[1][0] == '-' ? 1 : 2;

    std::string arg;
    for(; i < argc; ++i) {
        arg = argv[i];

        if(arg == "-h" || arg == "--help") {
            help();
            return 0;
        } else if(arg == "-d" || arg == "--debug") {
            // TODO: Set rule ENABLE_DEBUG
        } else {
            filenames.push_back(arg);
        }
    }

    for(auto& filename : filenames) {
        try {
            parse(filename, lib_obj_name, epy_list);
        } catch(...) {
            std::cerr << "A fatal error occurred for generate(" << filename
                      << ", " << lib_obj_name << ")" << std::endl;
            return 1;
        }
    }

    for(auto& epy : epy_list) {
        generate(epy);
    }

    return 0;
}

