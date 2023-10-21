#pragma once

#include <stdexcept>
#include <ostream>
#include <istream>
#include <cmath>

namespace piradio
{
  class frequency
  {
  public:
    frequency(double _f=0.0) : f(_f) { }

    frequency(const std::string &);
    
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
    double af = std::abs(f.Hz());
      
    if (af < 1e3) {
      out << f.Hz() << "Hz";
    } else if (af < 1e6) {
      out << f.KHz() << "KHz";
    } else if (af < 1e9) {
      out << f.MHz() << "MHz";
    } else {
      out << f.GHz() << "GHz";
    }

    return out;
  }

  static inline std::istream &operator>>(std::istream &in, frequency &f)
  {
    double d;

    in >> d;

    auto c = in.peek();

    double mult = 1.0;

    if (c == 'G') {
      in.get(); mult = 1e9;
    } else if (c == 'M') {
      in.get(); mult = 1e6;
    } else if (c == 'K') {
      in.get(); mult = 1e3;
    }
    
    if (in.get() != 'H') throw std::runtime_error("Badly formatted freqeuency");      
    if (in.get() != 'z') throw std::runtime_error("Badly formatted freqeuency");      

    f = frequency(d * mult);
    
    return in;
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
