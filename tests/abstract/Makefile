CXX=clang++

ifeq ($(OS),Windows_NT)
LFLAGS=C:/Python364/libs/python36.lib
INCLUDES=-IC:/Python364/include -I.
CXXFLAGS=-std=c++17 -g -Xclang -flto-visibility-public-std $(INCLUDES) -DHAVE_CONFIG_H -m32 -Wno-return-type

DLL_OUT=ABS.dll
LIB_OUT=ABS.lib

EPYGEN=../../EpyGen.bat

else
LFLAGS:=$(shell python3-config --ldflags)
INCLUDES:=$(shell python3-config --includes) -I.
CXXFLAGS=-std=c++17 -g -Xclang -flto-visibility-public-std $(INCLUDES) -Wno-return-type -fPIC

DLL_OUT=libABS.so
LIB_OUT=-L. -lABS

EPYGEN=../../EpyGen.sh
endif

SOURCES=ABS.cpp ABS_wrap.cpp

CXXSOURCES=$(SOURCES)
CXXOUTS=$(patsubst %.cpp,%.o,$(CXXSOURCES))

all: | epy library
	@echo

library: $(CXXSOURCES)
	$(CXX) $(LFLAGS) $(CXXFLAGS) -DEXPORT -shared $(CXXSOURCES) -o $(DLL_OUT)

epy: ABS.epy
	$(EPYGEN) libABS.so ABS.epy

