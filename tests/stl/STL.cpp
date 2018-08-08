
#include "STL.h"

std::vector<int> GetVector() {
    return std::vector<int>{5, 4, 3, 2, 1};
}

std::map<int, float> GetMap() {
    std::map<int, float> map;
    map[5] = 4.3f;
    map[4] = 25;
    map[3] = 100;

    map[1231] = 12345;

    return map;
}

std::string GetString() {
    return "This is a string returned from GetString()";
}

std::tuple<int, float, std::string, double> GetTuple() {
    return std::tuple<int, float, std::string, double>{5, 2.5f, "ffdasd", 3.7};
}
