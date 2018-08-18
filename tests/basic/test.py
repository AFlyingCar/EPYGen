import lib.Test as T

def foo(a,b):
    print("{0} + {1} = {2}".format(a,b,a+b))
    return int(a + b)

myHello = T.Hello("foobar")

print(myHello.say())
myHello.mparam(5,3)

myHello.fparam(foo)

try:
    T.Hello.throwTest()
except Exception as e:
    print("Caught {0} from T.Hello.throwTest().".format(str(e)))

T.Hello.sayHello()
myHello.sayHello()

del myHello

