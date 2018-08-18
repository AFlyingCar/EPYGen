# -*- coding: utf-8 -*-
# @Author: Tyler Robbins
# @Date:   2018-07-29 20:29:15

import Type, Parse, Section, Constants

def CPPTypeToCType(cpptype): # TODO
    return cpptype

##
# @brief Generates a C++ null pointer check.
#
# @param ident The indentation count.
# @param var The variable name the check is being generated for.
# @param fname The name of the function this check exists in.
#
# @return A string containing C++ code for a null pointer check.
#
def createCPPNullCheck(ident, var, fname):
    return ("    " * ident + "if({0} == nullptr) {{\n" +\
            "    " * ident + "    PyErr_SetString(PyExc_ValueError, \"Null pointer given for parameter {0} in function {1}\");\n" +\
            "    " * ident + "    return nullptr;\n" +\
            "    " * ident + "}}\n").format(var, fname)

##
# @brief Creates a Python object name for exceptions if a default one does not already exist.
#
# @param t The C++ exception type.
#
# @return The name of a C++ Py_Object representing an exception in Python.
#
def createCPPPyExceptionObjectName(t):
    if t in Constants.CPP_PY_EXCEPTION_MAPPING:
        return Constants.CPP_PY_EXCEPTION_MAPPING[t]
    else:
        return "_pywrapped_EXCEPTION_" + '_'.join(t.split('::'))

##
# @brief Generates a wrapper for a c++ exception
# @details This is required so that exceptions aren't thrown into CPython,
#          which does not handle C++ exceptions and would cause the entire stack
#          to be unwound back to where python was originally initialized.
#
# @param throw The name of the exception type that should be wrapped around.
# @param fname The name of the function this wrapper is being generated in.
#
# @return A string consisting of C++ code which handles an exception and raises
#         a python exception.
#
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

    # Make sure we create the Python exception object if it isn't a constant
    if throw not in Constants.CPP_PY_EXCEPTION_MAPPING:
        exc_wrapper += Constants.CPP_PY_OBJ_WRAPPER_CREATOR.format("    " * 3, exc_obj_name, py_nspaces, exc_name)

    exc_wrapper += "    " * 3 + "PyErr_SetString({0}, e.what());\n".format(exc_obj_name)
    exc_wrapper += "    " * 3 + "return 0;\n"

    return exc_wrapper

##
# @brief Generates a C-style function wrapper around a constructor for a class.
#
# @param klass_name The name of the class this constructor belongs to
# @param params A list of parameters in the following format: (Type:type, bool:is_default)
# @param throws A list of all exceptions this constructor may throw.
# @param epy The Epy object for this file.
# @param referenced_throws A list of all exceptions that have been referenced by
#                          this class.
# @param ctor_num Which constructor this is (used in case of multiple constructors).
# @param is_virtual Whether this class has any virtual methods in it.
#
# @return A string containing C++ code for a C-style function wrapper around a constructor.
#
def createCPPCtor(klass_name, params, throws, epy, referenced_throws = [], ctor_num = 0, is_virtual = False):
    ctor_str = "    "

    func_name = "{0}'s Constructor".format(klass_name)

    # Generate exception globals if they have not yet been referenced
    for t in throws:
        if t not in referenced_throws and t not in Constants.CPP_PY_EXCEPTION_MAPPING:
            ctor_str += "static PyObject* " + createCPPPyExceptionObjectName(t) + " = nulllptr;\n    "

            referenced_throws.append(t)

    if Constants.IS_WINDOWS:
        ctor_str += "__declspec(dllexport) "

    ctor_str += "void* _pywrapped_{0}_Create{1}(".format(klass_name, str(ctor_num) if ctor_num > 0 else "")

    if is_virtual:
        klass_name = "_pywrapped_{0}".format(klass_name)

    pcount = 0
    for p in params:
        ctor_str += p[0].c_type + ' param' + str(pcount) + ','
        pcount += 1

    if is_virtual:
        ctor_str += "PyObject* pyobj"

    if ctor_str.endswith(','):
        ctor_str = ctor_str[:-1]

    ctor_str += ") {\n"

    ctor_str += "    " * 2 + "try {\n"
    ctor_str += "    " * 3 + "return new {0}(".format(klass_name)

    pcount = 0
    for p in params:
        # Generate casts to cpp types
        # ctor_str += "{0}({1})".format(p[0].raw, 'param' + str(pcount)) + ","
        ctor_str += p[0].createCPPTransformation("", "(param" + str(pcount) + ")") + ","

    if is_virtual:
        ctor_str += "pyobj"

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

##
# @brief Generates the header of a C++ function wrapper.
#
# @param cres_type The result type of the function. Either a str or a Type.
# @param full_name The full of the function to generate.
# @param function The Function object containing information about this function.
# @param is_class Whether or not this function is a method in a class.
# @param is_virtual Whether or not this function is a virtual wrapper.
# @param use_raw_types Whether or not the raw C++ type should be used.
#
# @return A string containing a C++ function wrapper header.
#
def createCPPFunctionHeader(cres_type, full_name, function, is_class, is_virtual = False, use_raw_types = False):
    func_header = ""

    # Don't generate the declspec call on virtual functions (those defined in a class wrapper)
    if Constants.IS_WINDOWS and not is_virtual:
        func_header += "__declspec(dllexport) "

    if type(cres_type) == str:
        func_header += cres_type + " "
    else:
        if cres_type.is_array:
            func_header += "void "
        else:
            func_header += cres_type.c_type + ' '
    func_header += full_name + "("

    # Generate parameter listing

    if is_class and not function.static:
        if function.const:
            func_header += "const "
        func_header += "void* self,"

    pcount = 0
    for p in function.param_list:
        if use_raw_types:
            p_type = p[0].raw
        else:
            p_type = p[0].c_type
        func_header += p_type + ' param' + str(pcount) + ','
        pcount += 1

    if type(cres_type) != str:
        if cres_type.is_array:
            func_header += cres_type.toCArrayOutputParams().format("result")

    if func_header.endswith(','):
        func_header = func_header[:-1] # Remove the trailing ,

    func_header += ")"
    return func_header

##
# @brief Generates a C-style function wrapper around a C++ function.
#
# @param full_name The full name of the C-style function wrapper.
# @param name The name of the original C++ function.
# @param function The Function object.
# @param epy The Epy object for this file.
# @param referenced_throws A list of all exceptions that have been referenced by
#                          this class.
# @param is_class Whether this function is a method in a class.
#
# @return A string containing a C-style function wrapper for a C++ function.
#
def createCPPFunction(full_name, name, function, epy, referenced_throws = [], is_class = False, ident = 0):
    func_string = '    ' * ident
    cres_type = CPPTypeToCType(function.rtype)

    # Generate exception globals if they have not yet been referenced
    for t in function.throws:
        if t not in referenced_throws and t not in Constants.CPP_PY_EXCEPTION_MAPPING:
            func_string += "static PyObject* " + createCPPPyExceptionObjectName(t) + " = nullptr;\n    "

            referenced_throws.append(t)

    # Generate header
    func_string += createCPPFunctionHeader(cres_type, full_name, function, is_class) + " {\n"

    has_ret_val = (cres_type.raw != "void")
    # Generate contents
    if is_class and not function.static:
        func_string += createCPPNullCheck(2, "self", name)

    func_string += "    " * (ident + 1) + "try {\n"
    func_string += "    " * (ident + 2)

    if has_ret_val:
        func_string += "return "

    call = ""

    if is_class:
        if function.static:
            call += "{0}::".format(function.owner.name)
        else:
            call += "(({0}*)self)->".format(("const " if function.const else "") + function.owner.name)

    if function.virtual:
        name = "Hello::" + name

    call += "{0}(".format(name)

    pcount = 0
    for p in function.param_list:
        # Generate casts to cpp types
        call += "{0}({1})".format(p[0].raw, p[0].createCTransformation('param' + str(pcount))) + ","

    if call.endswith(','):
        call = call[:-1] # Remove the trailing ,
    call += ")"

    if has_ret_val:
        call = cres_type.createCTransformation(call, '    ' * (ident + 2))

    func_string += call + ";\n"

    for t in function.throws:
        func_string += createCPPPyExceptionWrapper(t, name)

    func_string += ("    " * (ident + 1)) + "} catch (...) {\n"
    func_string += ("    " * (ident + 2)) + "PyErr_SetString(PyExc_RuntimeError, \"An unspecified exception has occurred in {0}\");\n".format(name)
    func_string += ("    " * (ident + 2)) + "return nullptr;\n"
    func_string += ("    " * (ident + 1)) + "}\n"

    func_string += ("    " * ident) + "}\n"

    return func_string

##
# @brief Generates a Virtual function wrapper.
#
# @param func The Function object.
# @param orig_name The name of the original class.
#
# @return A string containing a wrapper for a virtual C++ function.
#
def createCPPVirtualFuncWrapper(func, orig_name):
    vfunc_str = ""
    ident = "    " * 2

    # Make sure we don't return references, as we do not hold onto the lifespan
    #  here
    # Note: This is a temporary fix, but I just don't really know how to properly
    #  handle references yet. Fix ASAP as virtual functions that return references
    #  cannot be exposed.
    # rtype = func.rtype.cpp_type if func.rtype.is_reference else func.rtype.raw
    rtype = func.rtype.raw

    # We pass False for is_class so that no `self` parameter gets generated
    vfunc_str += ident + createCPPFunctionHeader(rtype, func.name, func, False, True, True)
    vfunc_str += (" const" if func.const else "") + " override {\n"

    ident += "    "

    param_str = ", ".join([p[0].createCTransformation('param' + str(i)) for i,p in enumerate(func.param_list, 0)])

    vfunc_str += ident + "if(m_pyobj != nullptr){\n"
    vfunc_str += ident + "    PyObject* result = PyObject_CallMethodObjArgs(m_pyobj, PyBytes_FromString(\"{0}\"), {1}".format(func.name, param_str)
    vfunc_str += (',' if param_str and not param_str.endswith(',') else '') + "NULL);\n"
    # Return PyObject as CPP type here
    if str(func.rtype).strip() != "void":
        vfunc_str += ident + "    return std::move(" + func.rtype.createPyObjectTransformation("","({0})".format("result")) + ");\n"
        # vfunc_str += ident + "    return Epy::PyObjectToType<{0}>(result);\n".format(func.rtype.raw)

    vfunc_str += ident + "} else {\n"
    if not func.abstract:
        vfunc_str += ident + "    {3}{0}::{1}({2});\n".format(orig_name, func.name, param_str, "return " if str(func.rtype).strip() != "void" else "")
    else:
        vfunc_str += ident + "    PyErr_SetString(PyExc_NotImplementedError, \"Cannot call {0} as it is abstract.\");\n".format(orig_name)
        if str(func.rtype).strip() != "void":
            vfunc_str += ident + "    return nullptr;\n"
    vfunc_str += ident + "}\n"

    ident = "    " * 2
    vfunc_str += ident + "}\n"

    return vfunc_str

##
# @brief A wrapper around a C++ constructor for use in C++ class wrappers.
#
# @param orig_name The original name of the class
# @param wrap_name The wrapped name of the class
# @param ctor A tuple representing the constructor to generate.
#
# @return A string containing a wrapper for a C++ constructor.
#
def createCPPClassWrapperCtor(orig_name, wrap_name, ctor):
    ctor_str = "        {0}(".format(wrap_name)
    # Generate Constructor Params
    pcount = 0
    for p in ctor[0]:
        ctor_str += p[0].raw + ' param' + str(pcount) + ','
        pcount += 1

    ctor_str += "PyObject* pyobj): "

    line_up = len(ctor_str)

    ctor_str += "{0}({1}),\n".format(orig_name, ', '.join(['param' + str(i) for i in range(pcount)]))
    # Pass parameters to original constructor

    ctor_str += (" " * line_up) + "m_pyobj(pyobj)\n"
    ctor_str += "        { }\n"

    return ctor_str
##
# @brief A wrapper around a C++ class for dealing with polymorphism.
#
# @param orig_name The original name of the class
# @param wrap_name The wrapped name of the class
# @param klass The Class object to generate a wrapper for
#
# @return A string containing a wrapper for a C++ class.
#
def createCPPClassWrapper(orig_name, wrap_name, klass):
    class_string = ""

    # Use structure so we don't havve to deal with accessors
    class_string += "class {0}: public {1} {{\n".format(wrap_name, orig_name)
    class_string += "    public:\n"
    for c in klass.ctors:
        class_string += createCPPClassWrapperCtor(orig_name, wrap_name, c)
    class_string += "        ~{0}() {{ }}\n".format(wrap_name)

    for f in klass.virtual_funcs:
        # Generate a function wrapper for every virtual function which handles
        #  whether to use the Python function or the C++ one
        class_string += createCPPVirtualFuncWrapper(f, orig_name)

    class_string += "    private:\n"
    class_string += "       PyObject* m_pyobj;\n"

    class_string += "};\n"

    return class_string

##
# @brief Generates all wrappers for a C++ class.
#
# @param klass The Class object to generate wrappers for.
# @param epy The Epy object for this file.
# @param reffed_throws A list of all throws referenced in this file.
#
# @return A string containing all wrappers for the given Class object.
#
def createCPPClass(klass, epy, reffed_throws):
    class_string = ""

    class_name = klass.name

    is_virtual = len(klass.virtual_funcs) > 0

    if is_virtual:
        wrapped_name = "_pywrapped_" + class_name
        class_string += createCPPClassWrapper(class_name, wrapped_name, klass)
        # class_name = wrapped_name

    class_string += "extern \"C\" {\n"

    ccount = 0
    for ctor in klass.ctors:
        class_string += createCPPCtor(class_name, ctor[0], ctor[2], epy, reffed_throws, ccount, is_virtual)
        ccount += 1

    if klass.dtor:
        class_string += Constants.CPP_DEL_FUNC.format("__declspec(dllexport)" if Constants.IS_WINDOWS else "", klass.name_fmt, klass.name)

    functions_found = {f.name: 0 for f in klass.functions}
    for f in klass.functions:
        if not f.abstract:
            full_name = klass.name_fmt + '_' + f.name + str(functions_found[f.name])
            class_string += createCPPFunction(full_name, f.name, f, epy, reffed_throws, True, 1)

    class_string += "}\n"

    return class_string

def createCPPNamespace(nspace, epy, reffed_throws):
    nspace_string = ""

    name = nspace.name
    ident = 1

    nspace_string += "extern \"C\" {\n"

    functions_found = {f.name: 0 for f in nspace.functions}
    for f in nspace.functions:
        full_name = nspace.name_fmt + '_' + f.name + str(functions_found[f.name])
        nspace_string += createCPPFunction(full_name, f.name, f, epy, reffed_throws, False, ident)

    nspace_string += "}"

    return nspace_string

##
# @brief Generates all C++ wrapping code for a given Epy file.
#
# @param epy The Epy object for this file.
#
# @return A string containing all C++ wrapping code for this file.
#
def generateCPP(epy):
    cplusplus = Constants.CPP_HEADER.format(Constants.VERSION, Constants.TODAY)

    reffed_throws = []

    for section in epy.sections:
        if type(section) is Section.Class:
            cplusplus += createCPPClass(section, epy, reffed_throws)
        elif type(section) is Section.Namespace:
            cplusplus += createCPPNamespace(section, epy, reffed_throws)
        elif type(section) is Parse.CppLiteral:
            cplusplus += section.literal

    return cplusplus

