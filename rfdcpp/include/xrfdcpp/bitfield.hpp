#pragma once
#include <stdint.h>
#include <stdlib.h>

namespace rfdc
{
  template <class n = volatile uint32_t> struct bitmask
  {
    static const size_t bits = sizeof(n) * 8;

    n val;
    n mask;

    n &apply(n &dst) {
      dst = (dst & ~mask) | (val & mask);

      return dst;
    }
  };
  
  template <int base, int len, class n = uint32_t> struct bitfield
  {
    static constexpr size_t bits = sizeof(n) * 8;
    
    n get(n v) const
    {
      return (v >> base) & ((1 << len) - 1);
    }
    
    volatile n &set(n &dst, volatile n &val) const
    {
      return mask(val).apply(dst);
    }

    n m(void) const
    {
      return ((1 << len) - 1) << base;
    }
    
    bitmask<n> mask(n & val) const
    {
      return bitmask((val << base) & m(), m());
    }
  };

}
