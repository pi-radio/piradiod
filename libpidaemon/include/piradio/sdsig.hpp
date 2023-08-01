#pragma once

namespace piradio
{
  template<typename A, typename... B>
  struct sdbus_type_sig
  {
    static const std::string sig(void) {
      return sdbus_type_sig<A>::sig() + sdbus_type_sig<B...>::sig(); 
    }
  };
  
  template<>
  struct sdbus_type_sig<int>
  {
    static const std::string sig(void) {
      return "i"; 
    }
  };
  
  template <typename R, typename... A>
  std::string sdbus_get_sig(std::function<R(A...)> &&f)
  {
    return sdbus_type_sig<A...>::sig();
  }
  
  template <typename R, typename... A>
  std::string sdbus_get_sig(R (*f)(A...))
  {
    return sdbus_type_sig<A...>::sig();
  }
};
