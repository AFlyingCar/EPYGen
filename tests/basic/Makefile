CXX=clang++

ifeq ($(OS),Windows_NT)
LFLAGS=C:/Python364/libs/python36.lib
INCLUDES=-IC:/Python364/include -I.
CXXFLAGS=-std=c++17 -g -Xclang -flto-visibility-public-std $(INCLUDES) -DHAVE_CONFIG_H -m32 -Wno-return-type

DLL_OUT=Test.dll
LIB_OUT=Test.lib

EPYGEN=../../EpyGen.bat

else
LFLAGS:=$(shell python3-config --ldflags)
INCLUDES:=$(shell python3-config --includes) -I.
CXXFLAGS=-std=c++17 -g -Xclang -flto-visibility-public-std $(INCLUDES) -Wno-return-type -fPIC

DLL_OUT=libTest.so
LIB_OUT=-L. -lTest

EPYGEN=../../EpyGen.sh
endif

SOURCES=lib/Test.cpp lib/Test_wrap.cpp

CXXSOURCES=$(SOURCES)
CXXOUTS=$(patsubst %.cpp,%.o,$(CXXSOURCES))

all: | epy library
	@echo

library: $(CXXSOURCES)
	$(CXX) $(LFLAGS) $(CXXFLAGS) -DEXPORT -shared $(CXXSOURCES) -o $(DLL_OUT)
	$(CXX) $(LFLAGS) $(CXXFLAGS) Main.cpp -o Test.exe $(LIB_OUT)

epy: lib/Test.epy
	$(EPYGEN) libTest.so lib/Test.epy

