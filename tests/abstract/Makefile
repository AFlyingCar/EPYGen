CXX=clang++

ifeq ($(OS),Windows_NT)
# LFLAGS=C:/Python364/libs/python36.lib
# INCLUDES=-IC:/Python364/include -I.
LFLAGS:=$(shell python -c "import os, sys; print(os.path.join(sys.exec_prefix, 'libs', 'python{0}{1}.lib'.format(sys.version_info.major, sys.version_info.minor)))")
INCLUDES:=-I$(shell python -c "import os, sys; print(os.path.join(sys.exec_prefix, 'include'))")
CXXFLAGS=-std=c++17 -g -Xclang -flto-visibility-public-std $(INCLUDES) -DHAVE_CONFIG_H -m32 -Wno-return-type

DLL_OUT=ABS.dll
LIB_OUT=ABS.lib

EPYGEN=..\..\EpyGen.bat
PYTHON=python

else
LFLAGS:=$(shell python3-config --ldflags)
INCLUDES:=$(shell python3-config --includes) -I.
CXXFLAGS=-std=c++17 -g -Xclang -flto-visibility-public-std $(INCLUDES) -Wno-return-type -fPIC

DLL_OUT=libABS.so
LIB_OUT=-L. -lABS

EPYGEN=../../EpyGen.sh
PYTHON=python3
endif

SOURCES=ABS.cpp ABS_wrap.cpp

CXXSOURCES=$(SOURCES)
CXXOUTS=$(patsubst %.cpp,%.o,$(CXXSOURCES))

all: | epy library
	@echo

library: $(CXXSOURCES)
	$(CXX) $(LFLAGS) $(CXXFLAGS) -DEXPORT -shared $(CXXSOURCES) -o $(DLL_OUT)

epy: ABS.epy
	$(EPYGEN) $(DLL_OUT) ABS.epy

run: | epy library
	$(PYTHON) ./test.py

