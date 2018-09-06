
import overload

print("===================")
print("print(overload.foo())")
print(overload.foo())

print("===================")
print("overload.foo(4, 3.0)")
overload.foo(4, 3.0)

print("===================")
print("print(overload.foo(0, 3.0, 56, 2.0))")
print(overload.foo(0, 3.0, 56, 2.0))

print("===================")
def a():
    return 25
print("print(overload.foo(a))")
print(overload.foo(a))

