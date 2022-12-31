#pragma once

#include <iostream>

namespace rfdc {
  template <class T>
  struct frequency
  {
    T f;
    
    frequency(T _f) : f(_f) {}
    
    static inline auto KHz(T v) {
      return frequency(v * 1000);
    }

    static inline auto MHz(T v) {
      return KHz(v * 1000);
    }

    static inline auto GHz(T v) {
      return MHz(v * 1000);
    }

    template <class U> frequency operator-(frequency<U> x) {
      return frequency(f - x.f);
    };

    template <class U> frequency &operator-=(frequency<U> x) {
      f -= x.f;
      return *this;
    };

    
    template <class U> frequency operator/(U x) {
      return frequency(f / x);
    };

    template <class U> frequency operator*(U x) {
      return frequency(f * x);
    };
  };

  typedef frequency<double> dfrequency;

  typedef std::tuple<frequency<double>, frequency<double>> dfrequency_limits;
  
  template <class T, class U>
  static inline auto operator *(U x, const frequency<T> &f)
  {
    return f * x;
  }
  
  template <class T>
  static inline std::ostream &operator <<(std::ostream &os, const frequency<T> &f)
  {
    if (f.f > 1e9) {
      os << f.f / 1e9 << " GHz";
    } else if(f.f > 1e6) {
      os << f.f / 1e6 << " MHz";
    } else if(f.f > 1e3) {
      os << f.f / 1e3 << " KHz";
    } else {
      os << f.f << " Hz";
    }

    return os;
  }
};
