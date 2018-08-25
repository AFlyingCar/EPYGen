
SOURCES=$(wildcard src/*.cpp)
INCLUDES=-Iinc/
OBJECTS=$(patsubst src/%.cpp,build/%.o,$(SOURCES))
CFLAGS=-Wall -Wextra -Werror -std=c++1z

CXX=clang++
OUT=EpyGen

all: $(OBJECTS)
	$(CXX) $(CFLAGS) $(OBJECTS) -o $(OUT)

build/%.o: src/%.cpp
	$(CXX) $(CFLAGS) $(INCLUDES) -c $< -o $@

clean:
	rm $(OBJECTS) $(OUT) 2>/dev/null

