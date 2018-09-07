# -*- coding: utf-8 -*-
# @Author: Tyler Robbins
# @Date:   2018-07-29 20:22:14

import re, os
import Type, Section

from Constants import ENABLE_DEBUG

CLASS_TYPE = 0
NSPACE_TYPE = 1
ENUM_TYPE = 2

class Function(object):
    def __init__(self, func, rtype, param_list, tparam_list, const, static, virtual, abstract, throws, owner):
        self.name = func
        self.rtype = rtype
        self.param_list = param_list
        self.tparam_list = tparam_list
        self.const = const
        self.static = static
        self.virtual = virtual
        self.abstract = abstract
        self.throws = throws
        self.owner = owner

class Operator(Function):
    def __init__(self, func, rtype, param_list, tparam_list, const, static, virtual, abstract, throws, owner):
        super().__init__(func, rtype, param_list, tparam_list, const, static, virtual, abstract, throws, owner)

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
        self.filename = filename
        self.lib = lib_name
        self.lib_name_fmt = formatLibName(lib_name)
        self.hasclasses = False
        self.hasenums = False

        self.parse(contents)

    def libIndirection(self):
        seps = self.filename.count(os.path.sep)
        return "os.path.join({0})".format(', '.join(['".."'] * seps)) if seps > 0 else '\'\''

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
        if ENABLE_DEBUG:
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

            if not type(state["sobj"]) is Section.Enum:
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

        if ENABLE_DEBUG:
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
                if ENABLE_DEBUG:
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
            if ENABLE_DEBUG:
                print("Found parameter `" + ptype + "`")
            params.append((Type.parseType(ptype.strip()), defaulted))

        if ENABLE_DEBUG:
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

        if ENABLE_DEBUG:
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
                if ENABLE_DEBUG:
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
            if ENABLE_DEBUG:
                print("Found parameter `" + ptype + "`")
            params.append((Type.parseType(ptype.strip()), defaulted))

        if ENABLE_DEBUG:
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
        if not type(state["sobj"]) is Section.Class:
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

        if ENABLE_DEBUG:
            print(throws_str)

        throws = self.parseThrowsStr(throws_str)

        if param_list is None:
            state["error"] = True
        else:
            default_overloads = []
            first_defaulted = next((i for i in range(len(param_list)) if param_list[i][1]), len(param_list))
            for i in range(first_defaulted, len(param_list) + 1):
                default_overloads.append((param_list[:i], tparam_list, throws, state["sobj"]))
            state["sobj"].ctors += default_overloads

        return state

    def parseDtorStatement(self, statement, state):
        if not type(state["sobj"]) is Section.Class:
            print("Internal Error: sobj is not Class")
            state["error"] = True
            return state

        state["sobj"].dtor = True

        return state

    def parseFunc(self, statement, state):
        isclass = False

        if type(state["sobj"]) is Section.Class:
            isclass = True
        elif type(state["sobj"]) is Section.Namespace:
            isclass = False
        else:
            print("Internal Error: sobj is `" + str(type(state["sobj"])) + "` not Class or Namespace")
            state["error"] = True
            return state

        func = statement[4:].lstrip()

        func, rtype = func.rsplit("->", 1)

        func = func.rstrip()
        rtype = rtype.lstrip()

        const = False
        static = False
        virtual = False
        abstract = False

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
            func = func[8:].lstrip()
        elif func.startswith("abstract "):
            if not isclass:
                print("Error: abstract only allowed on class sections.")
                state["error"] = True
                return state
            virtual = True
            abstract = True
            func = func[9:].lstrip()

        func_and_tparams, param_str = func.split('(', 1)
        if('<') in func_and_tparams:
            func, tparams = func_and_tparams.split('<')
            tparams = '<' + tparams
        else:
            func = func_and_tparams
            tparams = "<>"
        param_str = '(' + param_str.lstrip()

        if ENABLE_DEBUG:
            print("Parsing function `" + func + "` with rtype `" + rtype + "`, parameters",
                  param_str, "tparams", tparams, "and modifiers",
                  ("const " if const else ""), ("static " if static else ""),
                  ("virtual" if virtual else ""),
                  ("abstract" if abstract else ""))

        param_list, throws_str = self.parseParamList(param_str)
        tparam_list = self.parseTParams(tparams)

        throws = self.parseThrowsStr(throws_str)

        # Verify that there are no spaces in the function name
        if re.match('^[\w]+$', func) is None:
            print("Invalid function name `" + func + '`')
            state["error"] = True
            return state

        # Generate Function object and append to sobj
        if not func in state["sobj"].functions:
            state["sobj"].functions[func] = []

        default_overloads = []
        first_defaulted = next((i for i in range(len(param_list)) if param_list[i][1]), len(param_list))
        for i in range(first_defaulted, len(param_list) + 1):
            default_overloads.append(Function(func,
                                              Type.parseType(rtype),
                                              param_list[:i], tparam_list,
                                              const, static, virtual,
                                              abstract, throws,
                                              state["sobj"]))

        state["sobj"].functions[func] += default_overloads
        if virtual:
            if not func in state["sobj"].virtual_funcs:
                state["sobj"].virtual_funcs[func] = []
            state["sobj"].virtual_funcs[func] += default_overloads
        if abstract:
            state["sobj"].abstract = True

        return state

    def parseOperator(self, statement, state):
        isclass = False

        if type(state["sobj"]) is Section.Class:
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
        abstract = False

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
        elif func.startswith("abstract "):
            if not isclass:
                print("Error: abstract only allowed on class sections.")
                state["error"] = True
                return state
            virtual = True
            abstract = True
            func = func[9:].lstrip()

        func_and_tparams, param_str = func.split('(', 1)
        if('<') in func_and_tparams:
            func, tparams = func_and_tparams.split('<')
            tparams = '<' + tparams
        else:
            func = func_and_tparams
            tparams = "<>"
        param_str = '(' + param_str.lstrip()

        if ENABLE_DEBUG:
            print("Parsing function `" + func + "` with rtype `" + rtype + "`, parameters",
                  param_str, "tparams", tparams, "and modifiers",
                  ("const " if const else ""), ("static " if static else ""),
                  ("virtual" if virtual else ""),
                  ("abstract" if abstract else ""))

        param_list, throws_str = self.parseParamList(param_str)
        tparam_list = self.parseTParams(tparams)

        throws = self.parseThrowsStr(throws_str)

        if not func in state["sobj"].functions:
            state["sobj"].functions[func] = []
        # Generate Function object and append to sobj
        state["sobj"].functions[func].append(Operator(func, Type.parseType(rtype),
                                                      param_list, tparam_list,
                                                      const, static, virtual,
                                                      abstract, throws,
                                                      state["sobj"]))

        if abstract:
            state["sobj"].abstract = True

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

        state["sobj"] = Section.Class(state["sname"], tparams)

        return state

    def parseEnumStatement(self, statement, state):
        state["stype"] = ENUM_TYPE

        rest = statement[4:].lstrip()

        eclass = False
        if rest.startswith("class"):
            eclass = True
            rest = rest[5:].lstrip()

        state["sobj"] = Section.Enum(rest, eclass)

        return state

    def parseNamespaceStatement(self, statement, state):
        state["stype"] = NSPACE_TYPE

        name = statement[9:].lstrip()

        state["sobj"] = Section.Namespace(name)

        return state

    def parseEnumValue(self, statement, state):
        if not type(state["sobj"]) is Section.Enum:
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
    return '_'.join('_'.join(('_'.join(lib_name.split('.')).split('/'))).split('\\')).upper() # libfile.so.1 -> LIBFILE_SO_1
