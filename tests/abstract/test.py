
import ABS

try:
    MyA = ABS.ABS()
except:
    print("Caught an exception when trying to construct an ABS.ABS object.")

class B(ABS.ABS):
    def __init__(self):
        super().__init__()
        print("B()")
    def pure(self, p):
        print("B.pure({0})".format(p))
        return p

b = B()

ABS.ABS.sayHelloThere()
b.sayGK()

b.pure(5)

