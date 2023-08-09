#pragma once

#include <ostream>

namespace piradio
{
  class frequency
  {
  public:
    frequency(double _f=0.0) : f(_f) { }

    double Hz() const { return f; } 
    double KHz() const { return f / 1.0e3; }
    double MHz() const { return f / 1.0e6; }
    double GHz() const { return f / 1.0e9; }

    frequency operator+(const frequency &f2) const { return frequency(f+f2.f); }
    frequency operator-(const frequency &f2) const { return frequency(f+f2.f); }

    double operator*(const frequency &f) const  = delete;
    double operator/(const frequency &f2) const { return f / f2.f; }

    frequency operator*(double d) const { return frequency(f*d); }
    frequency operator/(double d) const { return frequency(f/d); }

    bool operator==(const frequency &other) const { return f == other.f; }
    
    auto operator<=>(const frequency &other) const { return f <=> other.f; }
    
  protected:
    double f;
  };

  static inline frequency operator*(double d, const frequency &f) { return f * d; }

  static inline std::ostream &operator<<(std::ostream &out, const frequency &f)
  {
    if (f.Hz() < 1000.0) {
      out << f.Hz() << "Hz";
    } else if (f.KHz() < 1000.0) {
      out << f.KHz() << "KHz";
    } else if (f.MHz() < 1000.0) {
      out << f.MHz() << "MHz";
    } else {
      out << f.GHz() << "GHz";
    }

    return out;
  }
  
  static inline frequency Hz(double f) { return frequency(f); }
  static inline frequency KHz(double f) { return frequency(f * 1.0e3); }
  static inline frequency MHz(double f) { return frequency(f * 1.0e6); }
  static inline frequency GHz(double f) { return frequency(f * 1.0e9); }

  class frequency_range
  {
  public:
    frequency_range(const frequency &_min, const frequency &_max) : min(_min), max(_max)
    {    
    }

    frequency bw(void) const { return max - min; }
  
    frequency lerp(double d) { return min + d * bw(); }

    double bc(const frequency &f) { return (f.Hz() - min.Hz()) / (max.Hz() - min.Hz()); }

    bool in_co(const frequency &f) { return (f >= min) && (f < max); }
    bool in_cc(const frequency &f) { return (f >= min) && (f <= max); }
  
  protected:
    frequency min, max;
  };
};
