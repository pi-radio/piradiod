#include <piradio/frequency.hpp>

namespace piradio
{
  frequency::frequency(const std::string &s)
  {
    std::size_t pos;

    f = std::stod(s, &pos);

    if (pos != s.length()) {
      auto suffix = s.substr(pos);
      std::string l = suffix;

      std::transform(l.begin(), l.end(), l.begin(),
		     [](unsigned char c){ return std::tolower(c); });
      
      if (l == "thz") {
	f *= 1e12;
      } else if (l == "ghz") {
	f *= 1e9;
      } else if (l == "mhz") {
	f *= 1e6;
      } else if (l == "khz") {
	f *= 1e3;
      } else if (l == "hz") {
      } else {
	throw std::runtime_error(std::string("Unknown frequency suffix ") + suffix);
      }
      
    }
  }
};
