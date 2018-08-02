# -*- coding: utf-8 -*-

# sys.argv
import sys

import Type, Parse, Section, CppGenerate, PyGenerate, Constants

""" The version magic variable. """
__version__ = Constants.VERSION

"""
Handles the parsing and generation for a single Epy file.

@param filename The full path to the Epy file to parse and generate from.
@param lib_obj_name The name of the library object file to use.
"""
def generate(filename, lib_obj_name):
    # Parse the Epy file
    epy = Parse.Epy(filename, open(filename).read().strip(), lib_obj_name.replace('\\', '\\\\'))

    if Constants.ENABLE_DEBUG:
        print("EPY\n===")
        print("has class:", epy.hasclasses)
        print("has enum:", epy.hasenums)

        for s in epy.sections:
            print(s)

    # Generate all Python code
    python = PyGenerate.generatePython(epy)

    if Constants.ENABLE_DEBUG:
        print("PYTHON\n======\n")
        print(python)

    # Generate all C++ code
    cpp = CppGenerate.generateCPP(epy)

    if Constants.ENABLE_DEBUG:
        print("CPP\n===\n")
        print(cpp)

    # Determine where the python and C++ files will be written to.
    py_name = filename[:-3] + "py"
    cpp_name = filename[:-4] + "_wrap.cpp"

    # Write them!
    if Constants.ENABLE_DEBUG:
        print("Writing to " + py_name)
    open(py_name, 'w').write(python)

    if Constants.ENABLE_DEBUG:
        print("Writing to " + cpp_name)
    open(cpp_name, 'w').write(cpp)

"""
Defines the main function of the program.
"""
def main():
    if(len(sys.argv) < 3):
        print("Invalid number of arguments.")
        return

    lib_obj_name = sys.argv[1]
    files = sys.argv[2:];

    for f in files:
        generate(f, lib_obj_name)

# The entry point
if __name__ == "__main__":
    main()
