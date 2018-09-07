# -*- coding: utf-8 -*-
# @Author: Tyler Robbins
# @Date:   2018-07-29 20:31:30

import Type, Parse, Section, Constants

from Constants import ENABLE_DEBUG

def createPyTypeCheck(param_name, type, ident = ""):
    return Constants.PY_TYPE_CHECK.format(ident, param_name, type.py_type, type.createPyTransformation(param_name))

def createPyTypeList(param_list):
    return "[{0}]".format(','.join([p[0].py_type for p in param_list]))

def createPyABCFunction(name, function, starting_ident = 1):
    if ENABLE_DEBUG:
        print("Creating Abstract Base Class function")

    ident = '    ' * starting_ident

    f_str = ident + "@abstractmethod\n"
    f_str += ident + "def {0}(self,{1}):\n".format(name, ','.join(['param' + str(i) for i in range(len(function.param_list))]))
    f_str += ident + '    pass\n'

    return f_str

def createPyFunction(cname, name, function, epy, count = 0, is_class = False, starting_ident = 0):
    if ENABLE_DEBUG:
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
        func_str += createPyTypeCheck('param' + str(i), p[0], ident)
        i += 1

    func_str += ident + "{0}{1}(".format("result = " if function.rtype.raw else "", cname)

    if is_class:
        params = params[1:] # Remove cls/self as we no longer need it and don't want
                            #  to pass it to the function
        if not function.static:
            params = ["ctypes.c_void_p(self.cobj)"] + params

    for i in range(len(params) - 1):
        params[i + 1] = "{0}({1})".format(function.param_list[i][0].py_c_type, 'param' + str(i))

    param_str = ", ".join(params)

    func_str += param_str + ')\n'

    if function.rtype.raw != "void":
        func_str += ident + "return result\n"

    return func_str

def createPyOverloads(name, overloads, nspace, epy, is_class = False, starting_ident = 0):
    # If there is only one function, then just do it the old fashioned way.
    if len(overloads) == 1:
        full_name = nspace.name_fmt + '_' + name + '1'
        return createPyFunction(full_name, name, overloads[0], epy, 1, False)
    else:
        if ENABLE_DEBUG:
            print("Creating function " + name)
        func_str = ""

        ident = ('    ' * starting_ident)

        params = ['*args']
        if is_class:
            if function.static:
                func_str += ident + "@classmethod\n"
                params = ["cls"] + params
            else:
                params = ["self"] + params

        func_str += (ident + "def {0}(" + ', '.join(params) + '):\n').format(name)

        starting_ident += 1
        ident += '    ' # Now that we are out of the function header, increase the indentation by one

        if is_class:
            func_str += "if self.cobj:\n"

            ident += "    "
            starting_ident += 1

        func_str += ident + "arg_tlist = [type(a) for a in args]\n" + ident
        ocount = 0
        for o in overloads:
            ocount += 1
            full_name = nspace.name_fmt + '_' + name + str(ocount)
            func_str += "if arg_tlist == {0} and {1}:\n".format(createPyTypeList(o.param_list), full_name)
            func_str += ident + "    {0}{1}(".format("result = " if o.rtype.raw else "", full_name)

            param_str = ', '.join((["ctypes.c_void_p(self.cobj)"] if is_class and not o.static else []) + ["{0}({1})".format(o.param_list[i][0].py_c_type, 'args[{0}]'.format(i)) for i in range(len(o.param_list))])

            func_str += param_str + ')\n'
            if o.rtype.raw != "void":
                func_str += ident + "    return result\n"
            func_str += ident + "el"
        func_str += "se:\n"
        func_str += ident + "    raise ValueError(\"No such overload found matching [{0}]\".format(', '.join([t.__name__ for t in arg_tlist])))\n"

        return func_str

def createPyFuncLoader(fname, rtype, params, lib_name, ident = ""):
    if ENABLE_DEBUG:
        print(fname,'->',rtype)
    return Constants.PY_FUNC_LOADER.format(ident, fname, lib_name,
                                 "\n{2}    {0}.restype = {1}".format(fname, rtype, ident) if rtype else "",
                                 ','.join([p[0] if type(p[0]) == str else p[0].py_c_type for p in params]))

def createPyCtor(ctor_list, klass, epy):
    # We have to make sure that we generate a default constructor so we have a
    #  self.cobj object in the generated class.
    if len(ctor_list) == 0:
        return "    def __init__(self):\n        self.cobj = {0}()\n".format(ctor_name)

    ctor_str = "    def __init__(self, *args):\n"

    ident = "    " * 2

    ctor_str += ident + "arg_tlist = [type(a) for a in args]\n" + ident

    ccount = 0
    for ctor in ctor_list:
        ccount += 1
        ctor_name = "_pywrapped_{0}_Create{1}".format(klass.name, ccount)

        ctor_str += "if arg_tlist == [{0}] and {1}:\n".format(", ".join([p[0].py_type for p in ctor[0]]), ctor_name)
        i = 0
        for p in ctor[0]:
            ctor_str += ident + "    param{0} = args[{1}]\n".format(i + 1, i)
            i += 1
        ctor_str += ident + "    self.cobj = {0}({1})\n".format(ctor_name, ", ".join(["param" + str(i + 1) for i in range(len(ctor[0]))] + ["self"] if len(klass.virtual_funcs) > 0 else []))
        ctor_str += ident + "el"

    ident = "    " * 2
    ctor_str += "se:\n"
    ctor_str += ident + "    raise ValueError(\"No such overload found matching [{0}]\".format(', '.join([t.__name__ for t in arg_tlist])))\n"
    # ctor_str += ident + "    self.cobj = None"

    return ctor_str

def createPyNamespace(nspace, epy):
    nspace_string = ""

    for name in nspace.functions:
        f_list = nspace.functions[name]
        # Just in case, skip over 0-length function lists
        if(len(f_list) != 0):
            nspace_string += createPyOverloads(name, f_list, nspace, epy)

    return nspace_string

def createPyClass(klass, epy):
    class_string = ""

    ctor_count = 0
    for c in klass.ctors:
        ctor_count += 1
        ctor_name = "_pywrapped_{0}_Create{1}".format(klass.name, str(ctor_count))
        params = c[0][:] # Make sure we take a copy of this list
        if len(klass.virtual_funcs) > 0:
            params += [("ctypes.py_object",)]
        class_string += createPyFuncLoader(ctor_name, "ctypes.c_void_p", params, epy.lib_name_fmt)

    if klass.dtor:
        class_string += createPyFuncLoader("{0}_Destroy".format(klass.name_fmt), "", [("ctypes.c_void_p",)], epy.lib_name_fmt)

    class_string += "class {0}({1}):\n".format(klass.name, "metaclass = ABCMeta" if klass.abstract else "object")

    class_string += createPyCtor(klass.ctors, klass, epy) + "\n"

    if klass.dtor:
        class_string += Constants.PY_DEL_FUNC.format(epy.lib_name_fmt, klass.name_fmt)

    for name in klass.functions:
        f_list = klass.functions[name]
        fcount = 0
        for f in f_list:
            fcount += 1
            if f.abstract:
                class_string += createPyABCFunction(name, f, fcount)
            else:
                full_name = klass.name_fmt + '_' + name + str(fcount)
                class_string += createPyFunction(full_name, name, f, epy,
                                                 fcount, True, 1)

    return class_string

def generatePython(epy):
    python = Constants.PYTHON_HEADER.format(Constants.VERSION, Constants.TODAY,
                                            epy.lib_name_fmt, epy.lib,
                                            epy.libIndirection())

    imported_abc = False

    for section in epy.sections:
        is_class = type(section) is Section.Class
        # Namespaces and classes both use the same code for their header
        if issubclass(type(section), Section.Namespace):
            for name in section.functions:
                f_list = section.functions[name]
                fcount = 0
                for f in f_list:
                    fcount += 1
                    if not f.abstract:
                        full_name = section.name_fmt + '_' + name + str(fcount)
                        python += createPyFuncLoader(full_name,
                                                     f.rtype.py_c_type,
                                                     ([("ctypes.c_void_p",)] if is_class and not f.static else []) + f.param_list,
                                                     epy.lib_name_fmt)

        if type(section) is Section.Class:
            # If this is the first abstract class, add an import for abc
            if section.abstract and not imported_abc:
                python += "\nfrom abc import ABCMeta, abstractmethod\n"
                imported_abc = True
            python += createPyClass(section, epy)
        elif type(section) is Section.Namespace:
            python += createPyNamespace(section, epy)
        elif type(section) is Parse.PyLiteral:
            python += section.literal

    return python
