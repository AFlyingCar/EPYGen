CXX=clang++

ifeq ($(OS),Windows_NT)
LFLAGS=C:/Python364/libs/python36.lib
INCLUDES=-IC:/Python364/include -I.
CXXFLAGS=-std=c++17 -g -Xclang -flto-visibility-public-std $(INCLUDES) -DHAVE_CONFIG_H -m32 -Wno-return-type

DLL_OUT=STL.dll
LIB_OUT=STL.lib

EPYGEN=../../EpyGen.bat

else
LFLAGS:=$(shell python3-config --ldflags)
INCLUDES:=$(shell python3-config --includes) -I.
CXXFLAGS=-std=c++17 -g -Xclang -flto-visibility-public-std $(INCLUDES) -Wno-return-type -fPIC

DLL_OUT=libSTL.so
LIB_OUT=-L. -lSTL

EPYGEN=../../EpyGen.sh
endif

PYTHON=python3

SOURCES=STL.cpp STL_wrap.cpp

CXXSOURCES=$(SOURCES)
CXXOUTS=$(patsubst %.cpp,%.o,$(CXXSOURCES))

all: | epy library
	@echo

library: $(CXXSOURCES)
	$(CXX) $(LFLAGS) $(CXXFLAGS) -DEXPORT -shared $(CXXSOURCES) -o $(DLL_OUT)

epy: STL.epy
	$(EPYGEN) $(DLL_OUT) STL.epy

run: | epy library
	$(PYTHON) ./test.py

