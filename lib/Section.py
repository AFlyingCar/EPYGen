def formatName(name):
    return "_pywrapped_" + ('_'.join(name.split('::')))

class Section(object):
    def __init__(self, name):
        self.name = name
        self.name_fmt = formatName(name)

    def __str__(self):
        return self.name

class Namespace(Section):
    def __init__(self, name):
        super().__init__(name)
        self.functions = []

    def __str__(self):
        s = super().__str__() + "\n"
        for f in self.functions:
            s += str(f) + "\n"

        return s

class Class(Namespace):
    def __init__(self, name, tparams):
        super().__init__(name)
        self.tparams = tparams

        # Tuple: (param_list, tparam_list, throws, Class)
        self.ctors = []
        self.virtual_funcs = []
        self.abstract = False

        # Nothing special needs to be done with the destructor, we just need to know that we have one
        self.dtor = False

    def __str__(self):
        s = super().__str__()
        for c in self.ctors:
            s += str(c) + "\n"
        return s

class Enum(Section):
    def __init__(self, name, eclass):
        super().__init__(name)

        self.eclass = eclass

        self.values = []

    def __str__(self):
        s = super().__str__() + "\n"
        for v in self.values:
            s += v[0] + "=" + v[1] + "\n"
        return s

