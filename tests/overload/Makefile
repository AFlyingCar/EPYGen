CXX=clang++

ifeq ($(OS),Windows_NT)
# LFLAGS=C:/Python364/libs/python36.lib
LFLAGS:=$(shell python -c "import os, sys; print(os.path.join(sys.exec_prefix, 'libs', 'python{0}{1}.lib'.format(sys.version_info.major, sys.version_info.minor)))")
INCLUDES:=-I$(shell python -c "import os, sys; print(os.path.join(sys.exec_prefix, 'include'))")
# INCLUDES=-IC:/Python364/include -I.
CXXFLAGS=-std=c++17 -g -Xclang -flto-visibility-public-std $(INCLUDES) -DHAVE_CONFIG_H -m32 -Wno-return-type

DLL_OUT=overload.dll
LIB_OUT=overload.lib

EPYGEN=..\..\EpyGen.bat
PYTHON=python

else
LFLAGS:=$(shell python3-config --ldflags)
INCLUDES:=$(shell python3-config --includes) -I.
CXXFLAGS=-std=c++17 -g -Xclang -flto-visibility-public-std $(INCLUDES) -Wno-return-type -fPIC

DLL_OUT=liboverload.so
LIB_OUT=-L. -loverload

EPYGEN=../../EpyGen.sh
PYTHON=python3
endif

SOURCES=overload.cpp overload_wrap.cpp

CXXSOURCES=$(SOURCES)
CXXOUTS=$(patsubst %.cpp,%.o,$(CXXSOURCES))

all: | epy library
	@echo

library: $(CXXSOURCES)
	$(CXX) $(LFLAGS) $(CXXFLAGS) -DEXPORT -shared $(CXXSOURCES) -o $(DLL_OUT)

epy: overload.epy
	$(EPYGEN) $(DLL_OUT) overload.epy

run: | epy library
	$(PYTHON) ./test.py

