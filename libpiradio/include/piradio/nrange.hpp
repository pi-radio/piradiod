#pragma once

namespace piradio
{
  class nrange
  {
  public:
    nrange(int _min, int _max) : min(_min), max(_max) {}

    // Someday we can use std::lerp
    int lerp(double f) { return min + f * (max - min); }
    
  protected:
    int min, max;
  };
}
