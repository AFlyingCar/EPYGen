# -*- coding: utf-8 -*-

import sys

import Type, Parse, Section, CppGenerate, PyGenerate, Constants

__version__ = Constants.VERSION

def generate(filename, lib_obj_name):
    epy = Parse.Epy(filename, open(filename).read().strip(), lib_obj_name.replace('\\', '\\\\'))

    if Constants.ENABLE_DEBUG:
        print("EPY\n===")
        print("has class:", epy.hasclasses)
        print("has enum:", epy.hasenums)

        for s in epy.sections:
            print(s)

    python = PyGenerate.generatePython(epy)

    if Constants.ENABLE_DEBUG:
        print("PYTHON\n======\n")
        print(python)

    cpp = CppGenerate.generateCPP(epy)

    if Constants.ENABLE_DEBUG:
        print("CPP\n===\n")
        print(cpp)

    py_name = filename[:-3] + "py"
    cpp_name = filename[:-4] + "_wrap.cpp"

    if Constants.ENABLE_DEBUG:
        print("Writing to " + py_name)
    open(py_name, 'w').write(python)

    if Constants.ENABLE_DEBUG:
        print("Writing to " + cpp_name)
    open(cpp_name, 'w').write(cpp)

def main():
    if(len(sys.argv) < 3):
        print("Invalid number of arguments.")
        return

    lib_obj_name = sys.argv[1]
    files = sys.argv[2:];

    for f in files:
        generate(f, lib_obj_name)

if __name__ == "__main__":
    main()
