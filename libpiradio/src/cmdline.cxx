#include <piradio/cmdline.hpp>

namespace piradio
{
  namespace CLI
  {
    template<>
    ValueWrapper<args_t &>::ValueWrapper(args_t &inargs) : v(inargs)
    {
    };
  };
};
