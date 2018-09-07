import re

import Constants

BUILTINS = ["bool", "int", "char", "float", "double"]

CPP_PY_TYPE_MAP = {
        "int": "int",
        "float": "float",
        "double": "float"
}

CPY_TYPE_MAP = {
        "int": "ctypes.c_int",
        "float": "ctypes.c_float",
        "double": "ctypes.c_double"
}

STRING   = 0
VECTOR   = 1
MAP      = 2
FUNCTION = 3

STL_MAP = {
        "std::string": STRING,
        "std::vector": VECTOR,
        "std::map": MAP,
        "std::function": FUNCTION,
}

def cppTupleToPyObjectTransformation(tup, prefix = ""):
    elements = ""

    ELEM_ADD_CONSTANT = "{0}    PyTuple_SetItem(tuple, {1}, {2});\n"

    i = 0
    for t in tup.tparams:
        var = "std::get<{0}>(tup)".format(i)
        elements += ELEM_ADD_CONSTANT.format(prefix, i, t.createCTransformation(var, '',"({0})".format(var), True))
        i += 1

    transformation = """[]({3} tup) -> PyObject* {{
{0}    PyObject* tuple = PyTuple_New({1});
{0}    if(!tuple) {{
{0}        PyErr_SetString(PyExc_MemoryError, "Unable to allocate enough memory for tuple elements.");
{0}        return Py_None;
{0}    }}
{2}{0}
{0}    return tuple;
{0}}}""".format(prefix, len(tup.tparams), elements, tup.raw)

    return transformation

class Type(object):
    def __init__(self, raw, is_const, namespaces, type_name, tparams, fparams, is_ptr, is_ptr_const, is_function):
        self.raw = raw
        self.is_array = False
        self.is_const = is_const
        self.namespaces = namespaces
        self.type_name = type_name
        self.tparams = tparams
        self.fparams = fparams
        self.is_ptr = is_ptr
        self.is_cptr = is_ptr_const
        self.is_function = is_function
        # We are a reference if we end with an &
        self.is_reference = raw.rstrip().endswith('&')
        self.becomes_pyobj = False

        name_parts = self.namespaces + [self.type_name] + list(map(str, self.tparams))
        self.full_name = '_'.join(name_parts)

        self.typedef = ""
        self.c_type = ""
        self.cpp_type = ""
        self.py_type = ""
        self.py_c_type = ""

        # If we are a std::function of things, then we are just going to become
        #  the first template parameter
        if self.full_name.startswith('std_function'):
            t = self.tparams[0]
            # We just don't override const in this case
            self.namespaces = t.namespaces
            self.type_name = t.type_name
            self.tparams = t.tparams
            self.fparams = t.fparams
            self.is_ptr = True # Make sure that functions are treated as pointers
            self.is_cptr = t.is_cptr
            self.is_function = t.is_function

            self.full_name = t.full_name

            self.typedef = t.typedef
            self.c_type = t.c_type
            self.cpp_type = t.cpp_type
            self.py_type = t.py_type
            self.py_c_type = t.py_c_type
        else:
            self.buildCType()
            self.buildCPPType()
            self.buildPyType()
            self.buildPyCType()

        if self.is_function:
            self.is_ptr = True

    def __str__(self):
        return self.full_name

    def toCArrayOutputParams(self):
        oparams = ""

        if self.full_name.startswith("std_vector"):
            oparams = "(" + self.tparams[0].c_type + ")* {0}_arr, size_t* {0}_size"
        elif self.full_name.startswith("std_map"):
            oparams = "(" + self.tparams[0].c_type + ")* {0}_key, size_t* {0}_keysize, " + \
                      "(" + self.tparams[1].c_type + ")* {0}_val, size_t* {0}_valsize"

        return oparams

    def createCTransformation(self, var, prefix = "", suffix = "", forceBP = False):
        if self.full_name == "std_string":
            suffix = "({0}.c_str())".format(var)
        if self.is_function:
            return "(({0}){1})".format(self.asCFunction(), var)
        elif self.becomes_pyobj or forceBP:
            return self.createToPyObjectTransformation(prefix, suffix)

        return var

    def createCPPTransformation(self, prefix = "", suffix = ""):
        if self.becomes_pyobj:
            return self.createPyObjectTransformation(prefix, suffix)
        return prefix + self.raw + suffix

    def createNull(self):
        if self.becomes_pyobj:
            return "Py_None"
        elif self.full_name == "std_string":
            return '""'
        elif self.is_function:
            return "[]({0}) -> {1} {{ return {2}; }}".format(','.join([p.c_type for p in self.fparams]), self.c_type, "0")
        else:
            return "0"

    def createPyTransformation(self, var):
        if self.py_type == "bytes":
            return "{0}.encode() if type({0}) is str else bytes({0})".format(var)
        elif self.is_function:
            return "None"
        else:
            return "{0}({1})".format(self.py_type, var)

    def asCFunction(self):
        return ("{0}(*)({1})").format(self.type_name, ','.join([p.type_name for p in self.fparams]))

    def createVoidStarTransformation(self, var):
        if self.full_name == "std_string":
            return "std::string((char*){0})".format(var)
        elif self.is_function:
            return "(({0})(({1}){2}))".format(self.raw, self.asCFunction(), var)
        else:
            return var

    def createPyObjectTransformation(self, prefix = "", suffix=""):
        transformation = ""
        failure = False

        if self.full_name == "std_string":
            transformation = "std::string({0}PyUnicode_AsUTF8{1})".format(prefix, suffix)
        elif self.full_name == "void": # Handle the case of a void type.
            return ""
        elif self.full_name in Constants.PRIMITIVES:
            return "Py{0}_As{0}{1}".format(Constants.PRIMITIVES[self.full_name].capitalize(), suffix)
        else:
            failure = True
            transformation = "nullptr;static_assert(false, \"Invalid PyObject transformation type: {0}\");".format(self.raw)

        if not failure and self.is_ptr and not self.is_reference:
            transformation = "new {0}({1})".format(self.cpp_type, transformation)

        return transformation

    # TODO: We need to get rid of `var`
    def createToPyObjectTransformation(self, prefix = "", suffix = ""):
        transformation = ""
        failure = False

        if self.full_name.startswith("std_vector"):
            if len(self.tparams) != 1:
                print("Template Error: STL Type `std::vector` must have 1 template parameter.");
            transformation = Constants.CPP_VECTOR_TO_PYOBJECT_TRANSFORMATION.format(
                    prefix, self.tparams[0].createToPyObjectTransformation(''), self.raw) + suffix
        elif self.full_name == "std_string":
            transformation = prefix + "PyBytes_FromString" + suffix
        elif self.full_name.startswith("std_map"):
            if len(self.tparams) != 2:
                print("Template Error: STL Type `std::map` must have 2 template parameters.")
            transformation = Constants.CPP_MAP_TO_PYOBJECT_TRANSFORMATION.format(
                    prefix, self.tparams[0].createToPyObjectTransformation(''),
                    self.tparams[1].createToPyObjectTransformation(''), self.raw) + suffix
        elif self.full_name.startswith("std_tuple"):
            # No need to check for tparam count here, as there are N params.
            transformation = cppTupleToPyObjectTransformation(self, prefix) + suffix
        elif self.full_name == "void": # Handle the case of a void type.
            return "Py_None"
        elif self.full_name in Constants.PRIMITIVES:
            transformation = prefix + Constants.PRIMITIVE_CONVERSION_FUNCTIONS[self.full_name] + suffix
        else:
            failure = True
            transformation = "nullptr;static_assert(false, \"Invalid PyObject transformation type: {0}\");".format(self.raw)

        return transformation

    def buildCType(self):
        # NOTE: If not a builtin, we should just return a void*, and let python handle
        #  the conversion

        #if self.full_name == "std_string" and (self.is_reference or self.is_ptr):
        #    self.c_type = "char"
        #    self.is_const = True # All strings are immutable
        if self.full_name.startswith("std_vector") or \
             self.full_name.startswith("std_map") or \
             self.full_name.startswith("std_tuple") or \
             self.full_name == "std_string":
            self.c_type = "PyObject"
            self.becomes_pyobj = True
            self.is_ptr = True
            self.is_reference = True
#        elif self.full_name.startswith("std_vector") or \
#             self.full_name.startswith("std_map"):
#            self.is_array = True
        else:
            self.c_type += self.full_name

        if self.is_function:
            self.c_type += "(*{0})(" + ','.join(map(str,self.fparams)) + ')'
            self.typedef = self.c_type
            self.c_type = "void*"

        if self.is_const:
            self.c_type = "const " + self.c_type

        if self.is_ptr:
            self.c_type += "*"
            if self.is_cptr:
                self.c_type += " const "
        else:
            # Make sure we are still a string
            if self.full_name == "std_string": self.c_type += "*"

    def buildCPPType(self):
        self.cpp_type = '::'.join(self.namespaces + [self.type_name])

    def buildPyType(self):
        if self.namespaces == ["std"] and self.type_name == "string":
            self.py_type = "str"
        elif self.namespaces == ["std"] and self.type_name == "vector":
            self.py_type = "list"
        elif self.namespaces == ["std"] and self.type_name == "tuple":
            self.py_type = "tuple"
        elif self.namespaces == ["std"] and self.type_name == "map":
            self.py_type = "dict"
        elif self.is_function:
            self.py_type = "types.FunctionType"
        elif self.full_name in BUILTINS:
            self.py_type = CPP_PY_TYPE_MAP[self.full_name]
        else:
            self.py_type = "object"

    def buildPyCType(self):
        if self.full_name.startswith("std_vector") or \
             self.full_name.startswith("std_map") or \
             self.full_name.startswith("std_tuple") or \
             self.full_name == "std_string":
            self.py_c_type = "ctypes.py_object"
        elif self.full_name in BUILTINS:
            self.py_c_type = CPY_TYPE_MAP[self.full_name]
        elif self.py_type == "object":
            self.py_c_type = "ctypes.c_void_p"

        if self.is_function:
            self.py_c_type = "ctypes.CFUNCTYPE({0}, {1})".format(self.py_c_type, ', '.join([i.py_c_type for i in self.fparams]))

    def generateCPPToCCast(self):
        return ""
    def generateCToCPPCast(self):
        return ""

def __parseType(type_str, idx = [0], sub = 0, function = 0):
    c = ''
    p_c = ''
    prev_token = ""
    token = ""
    namespaces = []
    tparams = []
    fparams = []
    is_const = False
    is_ptr = False
    is_const_ptr = False
    is_function = False
    t = ""

    while idx[0] < len(type_str):
        c = type_str[idx[0]]

        if c in " \n\t\r":
            prev_token = token
            if token == "const":
                is_const = True
                token = ""
        elif c == '*':
            if prev_token == "const":
                is_const_ptr = True
                is_ptr = True
            else:
                is_ptr = True
        elif c == '&':
            is_const_ptr = True
            is_ptr = True
        elif c == ':':
            namespaces.append(token.strip())
            token = ""
            idx[0] += 1
            if type_str[idx[0]] != ':':
                print("ERROR: Need two :")
                return None
        elif c == '<':
            if not t: # Set t to be token if it has not already been set
                t = token
            token = ""
            idx[0] += 1
            tp = __parseType(type_str, idx, sub + 1, function)
            if tp:
                tparams.append(tp)
            while type_str[idx[0]] == ',':
                idx[0] += 1
                tp = __parseType(type_str, idx, sub + 1, function)
                if tp:
                    tparams.append(tp)
        elif c == '>':
            if sub > 0:
                break
            else:
                print("ERROR: mismatched <>")
                return None
        elif c == '(':
            if not t: # Set t to be token if it has not already been set
                t = token
            token = ""
            idx[0] += 1
            f = __parseType(type_str, idx, sub, function + 1)
            if f:
                fparams.append(f)
            while type_str[idx[0]] == ',':
                idx[0] += 1
                f = __parseType(type_str, idx, sub, function + 1)
                if f:
                    fparams.append(f)
            is_function = True
        elif c == ')':
            if function > 0:
                break
            else:
                print("ERROR: mismatched ()")
            break
        elif c == ',':
            break
        else:
            token += c

        p_c = c
        idx[0] += 1

    # If the token is left all by itself, let's just pretend it was the type name,
    #  as there are no other valid possibilities for it to be
    if token:
        t = token.strip()

    if t:
        return Type(type_str, is_const, namespaces, t.strip(), tparams, fparams, is_ptr, is_const_ptr, is_function)
    else:
        return None

def parseType(type_str):
    return __parseType(type_str, [0], 0, 0)

if __name__ == "__main__":
    # Run tests here
    t = parseType("int")
    print(t.c_type)
    print(t.py_type)
    t = parseType("float&")
    print(t.c_type)
    print(t.py_type)
    t = parseType("std::vector<int>")
    print(t.c_type)
    print(t.py_type)
    t = parseType("std::map<int, float>")
    print(t.c_type)
    print(t.py_type)
    t = parseType("std::vector<std::map<int, std::vector<std::vector<char*>>>>")
    print(t.c_type)
    print(t.py_type)
    t = parseType("std::function<void(float, int)>")
    print(t.c_type)
    print(t.py_type)
    t = parseType("std::vector<int>()")
    print(t.c_type)
    print(t.py_type)

