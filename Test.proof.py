# -*- coding: utf-8 -*-

import ctypes

__LIBRARY_TEST__ = ctypes.CDLL("Test.dll")

class Hello(object):
    def __init__(self, param1 = None):
        self.cobj = None
        if param1:
            if type(param1) == str: param1 = str.encode(param1)
            self.cobj = getattr(__LIBRARY_TEST__, "__pywrapped_Hello_Create_1")(ctypes.c_char_p(param1))
        else:
            self.cobj = getattr(__LIBRARY_TEST__, "__pywrapped_Hello_Create")()

    def __del__(self):
        if self.cobj:
            getattr(__LIBRARY_TEST__, "__pywrapped_Hello_Destroy")(self.cobj)

    def say(self):
        if self.cobj:
            getattr(__LIBRARY_TEST__, "__pywrapped_Hello_say").restype = ctypes.c_char_p
            res = getattr(__LIBRARY_TEST__, "__pywrapped_Hello_say")(self.cobj)

            return res

    def mparam(self, param1, param2):
        if self.cobj:
            value1 = ctypes.c_int(param1)
            value2 = ctypes.c_float(param2)

            getattr(__LIBRARY_TEST__, "__pywrapped_Hello_mparam")(self.cobj, value1, value2)

            return None

    def fparam(self, param1):
        if self.cobj:
            value1 = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_float)()

            getattr(__LIBRARY_TEST__, "__pywrapped_Hello_fparam")(self.cobj, value1)

            return None
