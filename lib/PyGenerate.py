# -*- coding: utf-8 -*-
# @Author: Tyler Robbins
# @Date:   2018-07-29 20:31:30

import Type, Parse, Section, Constants

from Constants import ENABLE_DEBUG

def createPyTypeCheck(param_name, type, ident = ""):
    return Constants.PY_TYPE_CHECK.format(ident, param_name, type.py_type, type.createPyTransformation(param_name))

def createPyFunction(cname, name, function, epy, is_class = False, starting_ident = 0):
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
        func_str += createPyTypeCheck('param' + str(i), p[0], ident)
        i += 1

    func_str += ident + "result = {0}(".format(cname)

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

def createPyFuncLoader(fname, rtype, params, lib_name, ident = ""):
    if ENABLE_DEBUG:
        print(fname,'->',rtype)
    return Constants.PY_FUNC_LOADER.format(ident, fname, lib_name,
                                 "\n{2}    {0}.restype = {1}".format(fname, rtype, ident) if rtype else "",
                                 ','.join([p[0] if type(p[0]) == str else p[0].py_c_type for p in params]))

def createPyCtor(ctor_list, klass, epy):
    # Do not generate a constructor if none are defined
    if len(ctor_list) == 0:
        return ""

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

    ctor += ident + "if " + ctor_name + ":\n"
    ident += "    "

    # TODO: Add support for default parameters
    i = 0
    for p in ctor_list[0][0]:
        ctor += createPyTypeCheck('param' + str(i), p[0], ident)
        i += 1

    ctor += ident + "self.cobj = {0}(".format(ctor_name)

    # Skip the self parameter
    i = 0
    for p in params[1:]:
        ctor += "{0}({1}), ".format(ctor_list[0][0][i][0].py_c_type, p.split(' ')[0])
        # ctor += p.split(' ')[0] + ', '
        i += 1

    if len(klass.virtual_funcs) > 0:
        ctor += " self"

    ctor = ctor.rstrip()
    if ctor.endswith(','):
        ctor = ctor[:-1]
    ctor += ")\n"

    ident = "    " * 2
    ctor += ident + "else:\n"
    ctor += ident + "    self.cobj = None"

    return ctor

def createPyClass(klass, epy):
    class_string = ""

    ctor_count = 0
    for c in klass.ctors:
        ctor_name = "_pywrapped_{0}_Create{1}".format(klass.name, str(ctor_count) if ctor_count > 0 else "")
        params = c[0][:] # Make sure we take a copy of this list
        if len(klass.virtual_funcs) > 0:
            params += [("ctypes.py_object",)]
        class_string += createPyFuncLoader(ctor_name, "ctypes.c_void_p", params, epy.lib_name_fmt)
        ctor_count += 1

    class_string += createPyFuncLoader("{0}_Destroy".format(klass.name_fmt), "", [("ctypes.c_void_p",)], epy.lib_name_fmt)

    class_string += "class {0}(object):\n".format(klass.name)

    class_string += createPyCtor(klass.ctors, klass, epy)

    if klass.dtor:
        class_string += Constants.PY_DEL_FUNC.format(epy.lib_name_fmt, klass.name_fmt)

    # name -> countx
    functions_found = {f.name: 0 for f in klass.functions}

    for f in klass.functions:
        full_name = klass.name_fmt + '_' + f.name + str(functions_found[f.name])
        class_string += createPyFunction(full_name, f.name + str(functions_found[f.name]),
                                         f, epy, True, 1)
        functions_found[f.name] += 1

    return class_string

def generatePython(epy):
    python = Constants.PYTHON_HEADER.format(Constants.VERSION, Constants.TODAY, epy.lib_name_fmt, epy.lib)

    for section in epy.sections:
        is_class = type(section) is Section.Class
        # Namespaces and classes both use the same code for their header
        if issubclass(type(section), Section.Namespace):
            functions_found = {f.name: 0 for f in section.functions}
            for f in section.functions:
                full_name = section.name_fmt + '_' + f.name + str(functions_found[f.name])
                python += createPyFuncLoader(full_name, f.rtype.py_c_type, ([("ctypes.c_void_p",)] if is_class and not f.static else []) + f.param_list, epy.lib_name_fmt)

        if type(section) is Section.Class:
            python += createPyClass(section, epy)
        elif type(section) is Parse.PyLiteral:
            python += section.literal

    return python
