# -*- coding: utf-8 -*-

import Test

print("a.py")

myHello = Test.Hello("foobar")

print(myHello.say())

def foo(a,b):
    print("The result of {0} + {1} is {2}".format(a,b,a+b))

    return int(a+b)

myHello.fparam(foo)

try:
    myHello.throwTest()
except Exception as e:
    print("Caught an exception from myHello.throwTest:", e)

Test.Hello.sayHello()

myHello = Test.Hello("General Kenobi!")

print(myHello.say())

