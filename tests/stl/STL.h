
#include <vector>
#include <map>
#include <tuple>
#include <string>

#include "API.h"

API std::vector<int> GetVector();
API std::map<int, float> GetMap();
API std::string GetString();

API std::tuple<int, float, std::string, double> GetTuple();

