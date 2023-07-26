#pragma once

#include <map>
#include <string>

namespace piradio
{
  namespace rfdc
  {
    namespace str
    {
      class cstrmap : public std::map<int, std::string>
      {
      public:
	cstrmap(std::initializer_list<value_type> init) : std::map<int, std::string>(init) {}
	const std::string &operator [](int k) const { return this->at(k); }
      };
      
      extern const cstrmap mixer_modes;
      extern const cstrmap mixer_types;
      extern const cstrmap tile_types;
    };
  };
};
