# -*- coding: utf-8 -*-

import sys, re, datetime, os

from Section import *
import Type

__version__ = "EpyGen v1.0"

CLASS_TYPE = 0
NSPACE_TYPE = 1
ENUM_TYPE = 2

CPP_PY_EXCEPTION_MAPPING = {
    "std::exception": "PyExc_Exception",

    "std::bad_alloc": "PyExc_MemoryError",
    "std::bad_cast": "PyExc_TypeError",
    # "std::bad_exception": "",
    "std::bad_function_call": "PyExc_EnvironmentError", # TODO: Maybe?
    "std::bad_typeid": "PyExc_ValueError",
    "std::bad_weak_ptr": "PyExc_MemoryError",

    "std::logic_error": "PyExc_RuntimeError", # TODO: We should figure out a better error to use
    "std::domain_error": "PyExc_ValueError", # There is no specific domain error
    # "std::future_error": "",
    "std::invalid_argument": "PyExc_ValueError",
    "std::length_error": "PyExc_ValueError",
    "std::out_of_range": "PyExc_IndexError",

    "std::runtime_error": "PyExc_RuntimeError",
    "std::overflow_error": "PyExc_OverflowError",
    "std::range_error": "PyExc_ValueError", # There is no specific range error
    "std::regex_error": "PyExc_ValueError",
    "std::system_error": "PyExc_SystemError",
    "std::underflow_error": "PyExc_UnderflowError"
}

# Use PyDLL instead of CDLL:
#  https://bytes.com/topic/python/answers/701504-fatal-python-error-using-ctypes-python-exceptions
PYTHON_HEADER = """# -*- coding: utf-8 -*-

'''
This file was automatically generated by {0} on {1}.
Do not modify this file unless you know what you are doing.
'''

import ctypes, sys

__LIBRARY_{2}__ = ctypes.PyDLL(\"{3}\")
""" # TODO: Include copyright info section

CPP_HEADER = """/*
 * This file was automatically generated by {0} on {1}.
 *  Do not modify this file unless you know what you are doing.
 *
 */
#include <Python.h>
#include <stdexcept>
#include <exception>
""" # TODO: Include copyright info section

PY_DEL_FUNC = """
    def __del__(self):
        if self.cobj and {1}_Destroy:
            {1}_Destroy(self.cobj)
"""

PY_FUNC_LOADER = """{0}try:
{0}    {1}{2} = getattr(__LIBRARY_{3}__, "{2}")
{0}except AttributeError as e:
{0}    print(str(e), file=sys.stderr)
{0}    {1}{2} = None
"""

CPP_DEL_FUNC = """    {0} void {1}_Destroy(void* ptr) {{
        delete ({2}*)ptr;
    }}
"""

CPP_PY_OBJ_WRAPPER_CREATOR = """{0}if({1} == nullptr) {{
{0}    {1} = PyErr_NewException("{2}.{3}", nullptr, nullptr);
{0}    Py_INCREF({1});
{0}    PyModule_AddObject(PyImport_AddModule("__main__"), "{2}", {1});
{0}}}
"""

today = datetime.date.today().isoformat()
lib_obj_name = ""

is_windows = os.name == 'nt'

class Function(object):
    def __init__(self, func, rtype, param_list, tparam_list, const, static, virtual, throws, owner):
        self.name = func
        self.rtype = rtype
        self.param_list = param_list
        self.tparam_list = tparam_list
        self.const = const
        self.static = static
        self.virtual = virtual
        self.throws = throws
        self.owner = owner

class Operator(Function):
    def __init__(self, func, rtype, param_list, tparam_list, const, static, virtual, throws, owner):
        super().__init__(func, rtype, param_list, tparam_list, const, static, virtual, throws, owner)

class PyLiteral(object):
    def __init__(self, literal):
        self.literal = literal

class CppLiteral(object):
    def __init__(self, literal):
        self.literal = literal

class Epy(object):
    def __init__(self, filename, contents, lib_name):
        self.mod_name = ""
        self.sections = []
        self.lib = lib_name
        self.lib_name_fmt = formatLibName(lib_name)
        self.hasclasses = False
        self.hasenums = False

        self.parse(contents)

    def parse(self, contents):
        statement = ""
        state = {
            "in_literalpy": False,
            "in_literalcpp": False,
            "in_section": False,
            "sname": "",
            "sobj": None,
            "prev_c": ""
        }
        i = 0

        while i < len(contents):
            c = contents[i]

            if c == ";" and not (state["in_literalpy"] or state["in_literalcpp"]):
                state = self.parseStatement(statement.strip(), state)
                statement = ""
            elif c == "@":
                i += 1
                ppstatement = ""

                # Ignore non-linebreaking whitespace
                while contents[i] in " \t":
                    i += 1
                while contents[i] not in " \n\r\t":
                    ppstatement += contents[i]
                    i += 1

                if not ppstatement:
                    if state["in_literalpy"]:
                        state["in_literalpy"] = False
                        self.sections.append(PyLiteral(statement))

                        statement = ""
                    elif state["in_literalcpp"]:
                        state["in_literalcpp"] = False
                        self.sections.append(CppLiteral(statement))

                        statement = ""
                    else:
                        print("Error: Encountered closing @ when outside of literal block.")
                elif ppstatement == "py":
                    state["in_literalpy"] = True
                elif ppstatement == "cpp":
                    state["in_literalcpp"] = True
                elif ppstatement == "include":
                    # TODO
                    pass
                else:
                    print("Unrecognized ppstatement " + ppstatement)
                    return
            else:
                if c == "/" and not (state["in_literalpy"] or state["in_literalcpp"]):
                    i += 1
                    if contents[i] == "/":
                        while contents[i] != "\n":
                            i += 1
                        continue
                    elif contents[i] == "*":
                        j = i - 1
                        n = j

                        while not (contents[j] == "*" and contents[i] == "/"):
                            i += 1
                            j += 1

                        i += 1 # Increment one more time to get past that pesky closing /
                        continue

                statement += c
                state["prev_c"] = c
            i += 1

    def parseStatement(self, statement, state):
        print("Statement:", statement)

        if not state["in_section"] and not self.mod_name:
            self.mod_name = statement
        elif statement == "start":
            state["in_section"] = True
        elif statement == "end":
            state["in_section"] = False
            if state["sobj"]:
                self.sections.append(state["sobj"])
            else:
                print("Internal Error: sobj is None")
                state["error"] = True
                return state
        elif statement.startswith("class"):
            state = self.parseClassStatement(statement, state)
            self.hasclasses = True
        elif statement.startswith("namespace"):
            state = self.parseNamespaceStatement(statement, state)
        elif statement.startswith("enum"):
            state = self.parseEnumStatement(statement, state)
            self.hasenums = True
        elif statement.startswith("ctor"):
            if not state["sobj"]:
                print("Internal Error: sobj is None")
                state["error"] = True
                return state
            state = self.parseCtorStatement(statement, state)
        elif statement.startswith("dtor"):
            if not state["sobj"]:
                print("Internal Error: sobj is None")
                state["error"] = True
                return state
            state = self.parseDtorStatement(statement, state)
        elif statement.startswith("func"):
            if not state["sobj"]:
                print("Internal Error: sobj is None")
                state["error"] = True
                return state
            state = self.parseFunc(statement, state)
        elif statement.startswith("operator"):
            if not state["sobj"]:
                print("Internal Error: sobj is None")
                state["error"] = True
                return state
            state = self.parseOperator(statement, state)
        elif state["stype"] == ENUM_TYPE:
            value = self.parseEnumValue(statement, state)

            if not state["sobj"]:
                print("Internal Error: sobj is None")
                state["error"] = True
                return state

            if not type(state["sobj"]) is Enum:
                print("Internal Error: sobj is not Enum")
                state["error"] = True
                return state

            state["sobj"].values.append(value)

        return state

    def parseTParams(self, param_str):
        param_str = param_str.strip() # Just to be safe
        if not (param_str.startswith('<') and param_str.endswith('>')):
            print("Error: Template parameter lists must be surrounded with <>")
            return None

        print("parsing tparam list")

        param_str = param_str[1:-1]

        params = []

        pcount = 0
        ptype = ""
        defaulted = False
        i = 0
        while i < len(param_str):
            c = param_str[i]

            if c == ',' and pcount == 0:
                print("Found parameter `" + ptype + "`")
                params.append((Type.parseType(ptype.strip()), defaulted))
                ptype = ""
                defaulted = False
                i += 1 # skip over the comma
                continue
            elif c == '=':
                defaulted = True
                i += 1
                continue

            # Handle template parameters and function pointers
            elif c == '<':
                pcount += 1
            elif c == '(':
                pcount += 1
            elif c == '>':
                pcount -= 1
            elif c == ')':
                pcount -= 1

            ptype += c

            i += 1

        if ptype:
            print("Found parameter `" + ptype + "`")
            params.append((Type.parseType(ptype.strip()), defaulted))

        print("Found " + str(len(params)) + " template parameters")

        print("done")

        return params

    def parseParamList(self, param_str):
        param_str = param_str.strip() # Just to be safe

        throws_str = param_str[param_str.rfind(')') + 1:].strip()
        param_str = param_str[:param_str.rfind(')') + 1].strip()

        if not (param_str.startswith('(') and param_str.endswith(')')):
            print("Error: Parameter lists must be surrounded with ()")
            return None

        print("parsing param list")

        param_str = param_str[1:-1]

        params = []

        pcount = 0
        ptype = ""
        defaulted = False
        i = 0
        while i < len(param_str):
            c = param_str[i]

            if c == ',' and pcount == 0:
                print("Found parameter `" + ptype + "`")
                params.append((Type.parseType(ptype.strip()), defaulted))
                ptype = ""
                defaulted = False
                i += 1 # skip over the comma
                continue
            elif c == '=':
                defaulted = True
                i += 1
                continue

            # Handle template parameters and function pointers
            elif c == '<':
                pcount += 1
            elif c == '(':
                pcount += 1
            elif c == '>':
                pcount -= 1
            elif c == ')':
                pcount -= 1
            ptype += c

            i += 1

        if ptype:
            print("Found parameter `" + ptype + "`")
            params.append((Type.parseType(ptype.strip()), defaulted))

        print("Found " + str(len(params)) + " parameters")

        print("done")

        return params, throws_str

    def parseThrowsStr(self, throws_str):
        throws = []
        throws_str = throws_str.strip()
        if throws_str.startswith("throws "):
            throws = [t.strip() for t in throws_str[7:].strip().split(",")]

        return throws

    def parseCtorStatement(self, statement, state):
        if not type(state["sobj"]) is Class:
            print("Internal Error: sobj is `" + str(type(state["sobj"])) + "` not Class")
            state["error"] = True
            return state

        rest = statement[4:].lstrip()
        tparam_str, param_str = rest.split('(')
        tparam_str.rstrip()
        param_str = '(' + param_str.lstrip()
        if '<' in tparam_str:
            tparam_list = self.parseTParams(tparam_str)
        else:
            tparam_list = []

        param_list, throws_str = self.parseParamList(param_str)

        print(throws_str)

        throws = self.parseThrowsStr(throws_str)

        if param_list is None:
            state["error"] = True
        else:
            state["sobj"].ctors.append((param_list, tparam_list, throws, state["sobj"]))

        return state

    def parseDtorStatement(self, statement, state):
        if not type(state["sobj"]) is Class:
            print("Internal Error: sobj is not Class")
            state["error"] = True
            return state

        state["sobj"].dtor = True

        return state

    def parseFunc(self, statement, state):
        isclass = False

        if type(state["sobj"]) is Class:
            isclass = True
        elif type(state["sobj"]) is Namespace:
            isclass = False
        else:
            print("Internal Error: sobj is `" + str(type(state["sobj"])) + "` not Class")
            state["error"] = True
            return state

        func = statement[4:].lstrip()

        func, rtype = func.rsplit("->", 1)

        func = func.rstrip()
        rtype = rtype.lstrip()

        const = False
        static = False
        virtual = False

        # class specific parsing
        # We check the space after each one to make sure the keywords aren't part of the next token
        if func.startswith("const "):
            if not isclass:
                print("Error: const only allowed on class sections.")
                state["error"] = True
                return state
            const = True
            func = func[5:].lstrip()
        if func.startswith("static "):
            if not isclass:
                print("Error: static only allowed on class sections.")
                state["error"] = True
                return state
            static = True
            func = func[6:].lstrip()
        elif func.startswith("virtual "):
            if not isclass:
                print("Error: virtual only allowed on class sections.")
                state["error"] = True
                return state
            virtual = True
            func = func[6:].lstrip()

        func_and_tparams, param_str = func.split('(', 1)
        if('<') in func_and_tparams:
            func, tparams = func_and_tparams.split('<')
            tparams = '<' + tparams
        else:
            func = func_and_tparams
            tparams = "<>"
        param_str = '(' + param_str.lstrip()

        print("Parsing function `" + func + "` with rtype `" + rtype + "`, parameters",
              param_str, "tparams", tparams, "and modifiers",
              ("const " if const else ""), ("static " if static else ""),
              ("virtual" if virtual else ""))

        param_list, throws_str = self.parseParamList(param_str)
        tparam_list = self.parseTParams(tparams)

        throws = self.parseThrowsStr(throws_str)

        # Verify that there are no spaces in the function name
        if re.match('^[\w]+$', func) is None:
            print("Invalid function name `" + func + '`')
            state["error"] = True
            return state

        # Generate Function object and append to sobj
        state["sobj"].functions.append(Function(func, Type.parseType(rtype), param_list,
                                                tparam_list, const, static,
                                                virtual, throws, state["sobj"]))
        if virtual:
            state["sobj"].virtual_funcs.append(Function(func, Type.parseType(rtype), param_list,
                                                        tparam_list, const,
                                                        static, virtual, throws,
                                                        state["sobj"]))

        return state

    def parseOperator(self, statement, state):
        isclass = False

        if type(state["sobj"]) is Class:
            isclass = True
        else:
            print("Internal Error: sobj is `" + str(type(state["sobj"])) + "` not Class")
            state["error"] = True
            return state

        func = statement[8:].lstrip()

        func, rtype = func.rsplit("->", 1)

        func = func.rstrip()
        rtype = rtype.lstrip()

        const = False
        static = False
        virtual = False

        # class specific parsing
        # We check the space after each one to make sure the keywords aren't part of the next token
        if func.startswith("const "):
            if not isclass:
                print("Error: const only allowed on class sections.")
                state["error"] = True
                return state
            const = True
            func = func[5:].lstrip()
        if func.startswith("static "):
            if not isclass:
                print("Error: static only allowed on class sections.")
                state["error"] = True
                return state
            static = True
            func = func[6:].lstrip()
        elif func.startswith("virtual "):
            if not isclass:
                print("Error: virtual only allowed on class sections.")
                state["error"] = True
                return state
            virtual = True
            func = func[6:].lstrip()

        func_and_tparams, param_str = func.split('(', 1)
        if('<') in func_and_tparams:
            func, tparams = func_and_tparams.split('<')
            tparams = '<' + tparams
        else:
            func = func_and_tparams
            tparams = "<>"
        param_str = '(' + param_str.lstrip()

        print("Parsing function `" + func + "` with rtype `" + rtype + "`, parameters",
              param_str, "tparams", tparams, "and modifiers",
              ("const " if const else ""), ("static " if static else ""),
              ("virtual" if virtual else ""))

        param_list, throws_str = self.parseParamList(param_str)
        tparam_list = self.parseTParams(tparams)

        throws = self.parseThrowsStr(throws_str)

        # Generate Function object and append to sobj
        state["sobj"].functions.append(Operator(func, Type.parseType(rtype),
                                                param_list, tparam_list, const,
                                                static, virtual, throws,
                                                state["sobj"]))

        return state

    def parseClassStatement(self, statement, state):
        # Section Type = class
        state["stype"] = CLASS_TYPE

        # Parse name
        left = statement[5:].lstrip()
        tstart = left.find("<")
        tparams = []
        if tstart >= 0:
            tparams = self.parseTParams(left[tstart:])
            state["sname"] = left[:tstart]
        else:
            state["sname"] = left

        state["sobj"] = Class(state["sname"], tparams)

        return state

    def parseEnumStatement(self, statement, state):
        state["stype"] = ENUM_TYPE

        rest = statement[4:].lstrip()

        eclass = False
        if rest.startswith("class"):
            eclass = True
            rest = rest[5:].lstrip()

        state["sobj"] = Enum(rest, eclass)

        return state

    def parseNamespaceStatement(self, statement, state):
        state["stype"] = NSPACE_TYPE

        name = statement[9:].lstrip()

        state["sobj"] = Namespace(name)

        return type

    def parseEnumValue(self, statement, state):
        if not type(state["sobj"]) is Enum:
            print("Internal Error: Values cannot be specified outside of enumerations.")
            state["error"] = True
            return state

        if '=' in statement:
            name, default = statement.split('=')
            name = name.rstrip()
            default = default.lstrip()
        else:
            name = statement
            default = ""

        return (name, default)

def formatLibName(lib_name):
    return '_'.join(lib_name.split('.')).upper() # libfile.so.1 -> LIBFILE_SO_1

def CPPTypeToCType(cpptype):
    return cpptype

def createPyTypeCheck(param_name, type):
    return ""

def createPyFunction(cname, name, function, epy, is_class = False, starting_ident = 0):
    print("Creating function " + function.name)
    func_str = ""

    ident = ('    ' * starting_ident)

    params = ['param' + str(i) for i in range(len(function.param_list))]
    if is_class:
        if function.static:
            func_str += ident + "@classmethod\n"
            params = ["cls"] + params
        else:
            params = ["self"] + params

    func_str += (ident + "def {0}(" + ', '.join(params) + '):\n').format(function.name)

    starting_ident += 1
    ident += '    ' # Now that we are out of the function header, increase the indentation by one

    # func_str += ident + "global {0}\n".format(cname)
    func_str += ident + "if "


    if is_class:
        if not function.static:
            func_str += "self.cobj and "

    func_str += cname

    func_str += ":\n"
    ident += "    "
    starting_ident += 1

    # TODO: Add support for default parameters
    i = 0
    for p in function.param_list:
        func_str += createPyTypeCheck('param' + str(i), p)
        i += 1

    func_str += ident + "result = {0}(".format(cname)

    if is_class:
        params = params[1:] # Remove cls/self as we no longer need it and don't want
                            #  to pass it to the function
        if not function.static:
            params = ["self.cobj"] + params

    # TODO: Add casts to this
    param_str = ", ".join(params)

    func_str += param_str + ')\n'

    if function.rtype != "void":
        func_str += ident + "return result\n"

    return func_str

def createPyFuncLoader(fname, lib_name, is_class, ident = ""):
    return PY_FUNC_LOADER.format(ident, "self." if is_class else "", fname, lib_name)

def createPyCtor(ctor_list, klass, epy):
    params = ["self"]
    ctor = "    def __init__("

    # Generate parameter listing

    min_params = min([len(i[0]) for i in ctor_list])
    max_params = max([len(i[0]) for i in ctor_list])

    for i in range(min_params):
        params.append("param" + str(i))

    for i in range(max_params - min_params):
        params.append("param" + str(i) + " = None")

    ctor += ", ".join(params) + "):\n"

    ident = "    " * 2

    # Generate Create calls.
    ctor_name = "_pywrapped_{0}_Create".format(klass.name)
    ctor += ident + "self.cobj = {0}(".format(ctor_name)

    # Skip the self parameter
    for p in params[1:]:
        ctor += p.split(' ')[0] + ', '
    ctor = ctor.rstrip()
    if ctor.endswith(','):
        ctor = ctor[:-1]
    ctor += ")"

    return ctor

def createPyClass(klass, epy):
    class_string = ""

    ctor_count = 0
    for c in klass.ctors:
        ctor_name = "_pywrapped_{0}_Create{1}".format(klass.name, str(ctor_count) if ctor_count > 0 else "")
        class_string += createPyFuncLoader(ctor_name, epy.lib_name_fmt, False)
        ctor_count += 1

    class_string += createPyFuncLoader("{0}_Destroy".format(klass.name_fmt), epy.lib_name_fmt, False)

    class_string += "class {0}(object):\n".format(klass.name)

    class_string += createPyCtor(klass.ctors, klass, epy)

    if klass.dtor:
        class_string += PY_DEL_FUNC.format(epy.lib_name_fmt, klass.name_fmt)

    # name -> countx
    functions_found = {f.name: 0 for f in klass.functions}

    for f in klass.functions:
        full_name = klass.name_fmt + '_' + f.name + str(functions_found[f.name])
        class_string += createPyFunction(full_name, f.name + str(functions_found[f.name]),
                                         f, epy, True, 1)
        functions_found[f.name] += 1

    return class_string

def generatePython(epy):
    python = PYTHON_HEADER.format(__version__, today, epy.lib_name_fmt, epy.lib)

    for section in epy.sections:
        # Namespaces and classes both use the same code for their header
        if issubclass(type(section), Namespace):
            functions_found = {f.name: 0 for f in section.functions}
            for f in section.functions:
                full_name = section.name_fmt + '_' + f.name + str(functions_found[f.name])
                python += createPyFuncLoader(full_name, epy.lib_name_fmt, False)

        if type(section) is Class:
            python += createPyClass(section, epy)
        elif type(section) is PyLiteral:
            python += section.literal

    return python

def createCPPNullCheck(ident, var, fname):
    return ("    " * ident + "if({0} == nullptr) {{\n" +\
            "    " * ident + "    PyErr_SetString(PyExc_ValueError, \"Null pointer given for parameter {0} in function {1}\");\n" +\
            "    " * ident + "    return nullptr;\n" +\
            "    " * ident + "}}\n").format(var, fname)

def createCPPPyExceptionObjectName(t):
    if t in CPP_PY_EXCEPTION_MAPPING:
        return CPP_PY_EXCEPTION_MAPPING[t]
    else:
        return "_pywrapped_EXCEPTION_" + '_'.join(t.split('::'))

def createCPPPyExceptionWrapper(throw, fname):
    exc_wrapper = "    " * 2
    exc_obj_name = createCPPPyExceptionObjectName(throw)

    nspaces = throw.split('::')[:-1]
    exc_name = throw.split('::')[-1]

    # Just to be safe
    if not nspaces:
        nspaces = ["_"] # TODO: This should be something else

    # Convert things like std::except into std.except
    py_nspaces = '.'.join(nspaces)

    exc_wrapper += "}} catch(const {0}& e) {{\n".format(throw)
    if throw not in CPP_PY_EXCEPTION_MAPPING:
        exc_wrapper += CPP_PY_OBJ_WRAPPER_CREATOR.format("    " * 3, exc_obj_name, py_nspaces, exc_name)

    exc_wrapper += "    " * 3 + "PyErr_SetString({0}, e.what());\n".format(exc_obj_name)
    exc_wrapper += "    " * 3 + "return 0;\n"

    return exc_wrapper

def createCPPCtor(klass_name, params, throws, epy, referenced_throws = [], ctor_num = 0):
    ctor_str = "    "

    func_name = "{0}'s Constructor".format(klass_name)

    # Generate exception globals if they have not yet been referenced
    for t in throws:
        if t not in referenced_throws and t not in CPP_PY_EXCEPTION_MAPPING:
            ctor_str += "static PyObject* " + createCPPPyExceptionObjectName(t) + " = nulllptr;\n    "

            referenced_throws.append(t)

    if is_windows:
        ctor_str += "__declspec(dllexport) "

    ctor_str += "void* _pywrapped_{0}_Create{1}(".format(klass_name, str(ctor_num) if ctor_num > 0 else "")

    pcount = 0
    for p in params:
        ctor_str += p[0].c_type + ' param' + str(pcount) + ','
        pcount += 1

    if ctor_str.endswith(','):
        ctor_str = ctor_str[:-1]

    ctor_str += ") {\n"

    ctor_str += "    " * 2 + "try {\n"
    ctor_str += "    " * 3 + "return new {0}(".format(klass_name)

    pcount = 0
    for p in params:
        # Generate casts to cpp types
        ctor_str += "{0}({1})".format(p[0].raw, 'param' + str(pcount)) + ","

    if ctor_str.endswith(','):
        ctor_str = ctor_str[:-1] # Remove the trailing ,
    ctor_str += ");\n"

    for t in throws:
        ctor_str += createCPPPyExceptionWrapper(t, func_name)

    ctor_str += "    " * 2 + "} catch (...) {\n"
    ctor_str += "    " * 3 + "PyErr_SetString(PyExc_RuntimeError, \"An unspecified exception has occurred in {0}\");\n".format(func_name)
    ctor_str += "    " * 3 + "return nullptr;\n"
    ctor_str += "    " * 2 + "}\n"

    return ctor_str + "    }\n"

def createCPPFunction(full_name, name, function, epy, referenced_throws = [], is_class = False):
    func_string = "    "
    cres_type = CPPTypeToCType(function.rtype)
    # Generate header

    # Generate exception globals if they have not yet been referenced
    for t in function.throws:
        if t not in referenced_throws and t not in CPP_PY_EXCEPTION_MAPPING:
            func_string += "static PyObject* " + createCPPPyExceptionObjectName(t) + " = nulllptr;\n    "

            referenced_throws.append(t)

    has_ret_val = (cres_type.raw != "void")

    if is_windows:
        func_string += "__declspec(dllexport) "

    if cres_type.is_array:
        func_string += "void "
    else:
        func_string += cres_type.c_type + ' '
    func_string += full_name + "("

    # Generate parameter listing

    if is_class and not function.static:
        if function.const:
            func_string += "const "
        func_string += "void* self,"

    pcount = 0
    for p in function.param_list:
        func_string += p[0].c_type + ' param' + str(pcount) + ','
        pcount += 1

    if cres_type.is_array:
        func_string += cres_type.toCArrayOutputParams().format("result")

    if func_string.endswith(','):
        func_string = func_string[:-1] # Remove the trailing ,

    func_string += ") {\n"

    # Generate contents
    if is_class and not function.static:
        func_string += createCPPNullCheck(2, "self", name)

    func_string += "    " * 2 + "try {\n"
    func_string += "    " * 3

    if has_ret_val:
        func_string += "return "

    call = ""

    if is_class:
        if function.static:
            call += "{0}::".format(function.owner.name)
        else:
            call += "(({0}*)self)->".format(("const " if function.const else "") + function.owner.name)
    call += "{0}(".format(name)

    pcount = 0
    for p in function.param_list:
        # Generate casts to cpp types
        call += "{0}({1})".format(p[0].raw, p[0].createCTransformation('param' + str(pcount))) + ","

    if call.endswith(','):
        call = call[:-1] # Remove the trailing ,
    call += ")"

    if has_ret_val:
        call = cres_type.createCTransformation(call)

    func_string += call + ";\n"

    for t in function.throws:
        func_string += createCPPPyExceptionWrapper(t, name)

    func_string += "    " * 2 + "} catch (...) {\n"
    func_string += "    " * 3 + "PyErr_SetString(PyExc_RuntimeError, \"An unspecified exception has occurred in {0}\");\n".format(name)
    func_string += "    " * 3 + "return nullptr;\n"
    func_string += "    " * 2 + "}\n"

    func_string += "    }\n"

    return func_string

def createCPPClassWrapper(orig_name, wrap_name, klass):
    class_string = ""

    # Use structure so we don't havve to deal with accessors
    class_string += "class {0}: public {1} {\n    public:\n".format(wrap_name, orig_name)
    class_string += "        ~{0}() { }\n"

    for f in klass.virtual_funcs:
        # Generate a function wrapper for every virtual function which handles
        #  whether to use the Python function or the C++ one
        pass

    class_string += "}\n"

    return class_string

def createCPPClass(klass, epy, reffed_throws):
    class_string = ""

    class_name = klass.name

    if len(klass.virtual_funcs) > 0:
        wrapped_name = "_pywrapped_" + class_name
        class_string += createCPPClassWrapper(class_name, wrapped_name, klass)
        class_name = wrapped_name

    class_string += "extern \"C\" {\n"

    ccount = 0
    for ctor in klass.ctors:
        class_string += createCPPCtor(klass.name, ctor[0], ctor[2], epy, reffed_throws, ccount)
        ccount += 1

    if klass.dtor:
        class_string += CPP_DEL_FUNC.format("__declspec(dllexport)" if is_windows else "", klass.name_fmt, klass.name)

    functions_found = {f.name: 0 for f in klass.functions}
    for f in klass.functions:
        full_name = klass.name_fmt + '_' + f.name + str(functions_found[f.name])
        class_string += createCPPFunction(full_name, f.name, f, epy, reffed_throws, True)

    class_string += "}\n"

    return class_string

def generateCPP(epy):
    cplusplus = CPP_HEADER.format(__version__, today)

    reffed_throws = []

    for section in epy.sections:
        if type(section) is Class:
            cplusplus += createCPPClass(section, epy, reffed_throws)
        elif type(section) is CppLiteral:
            cplusplus += section.literal

    return cplusplus

def generate(filename):
    epy = Epy(filename, open(filename).read().strip(), lib_obj_name)

    print("EPY\n===")
    print("has class:", epy.hasclasses)
    print("has enum:", epy.hasenums)

    for s in epy.sections:
        print(s)

    python = generatePython(epy)

    print("PYTHON\n======\n")
    print(python)

    cpp = generateCPP(epy)

    # print("CPP\n===\n")
    # print(cpp)

    py_name = filename[:-3] + "py"
    cpp_name = filename[:-4] + "_wrap.cpp"

    print("Writing to " + py_name)
    open(py_name, 'w').write(python)

    print("Writing to " + cpp_name)
    open(cpp_name, 'w').write(cpp)

def main():
    if(len(sys.argv) < 3):
        print("Invalid number of arguments.")
        return

    global lib_obj_name
    lib_obj_name = sys.argv[1]
    files = sys.argv[2:];

    for f in files:
        generate(f)

if __name__ == "__main__":
    main()
