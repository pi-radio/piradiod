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
  
  template <class n = volatile uint32_t> struct bitfield
  {
    static const size_t bits = sizeof(n) * 8;
    
    uint32_t base;
    uint32_t len;

    bitfield(uint32_t _base, uint32_t _len) : base(_base), len(_len) {};

    n get(n &v) const
    {
      return (v >> base) & ((1 << len) - 1);
    }
    
    n &set(n &dst, n &val) const
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
