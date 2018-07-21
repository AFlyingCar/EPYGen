CXX=clang++

INCLUDES=-IC:/Python364/include -I.
CXXFLAGS=-std=c++17 -g -Xclang -flto-visibility-public-std $(INCLUDES) -DHAVE_CONFIG_H -m32 -Wno-return-type
LFLAGS=C:/Python364/libs/python36.lib

SOURCES=lib/Test.cpp lib/Foo.cpp lib/Test_wrap.cpp

CXXSOURCES=$(SOURCES)
CXXOUTS=$(patsubst %.cpp,%.o,$(CXXSOURCES))

all:  $(CXXSOURCES)
	$(CXX) $(LFLAGS) $(CXXFLAGS) -DEXPORT -shared $(CXXSOURCES) -o Test.dll
	$(CXX) $(LFLAGS) $(CXXFLAGS) Test.lib Main.cpp -o Test.exe
