#pragma once

namespace piradio
{
  template<typename...>
  struct sdbus_type_sig
  {
    static const std::string sig(void) {
      return ""; 
    }

    template <typename bindtype>
    static auto bind(bindtype b, sdbus::MethodCall call)
    {
      return b;
    }
  };
    
  template<typename A, typename... B>
  struct sdbus_type_sig<A, B...>
  {
    static const std::string sig(void) {
      return sdbus_type_sig<A>::sig() + sdbus_type_sig<B...>::sig(); 
    }

    template <typename bindtype>
    static auto bind(bindtype b, sdbus::MethodCall call)
    {
      return sdbus_type_sig<B...>::bind(sdbus_type_sig<A>::bind(b, call), call);
    }
  };

  template<>
  struct sdbus_type_sig<int>
  {
    static const std::string sig(void) {
      return "i"; 
    }

    template <typename bindtype>
    static auto bind(bindtype b, sdbus::MethodCall call)
    {
      int i;

      call >> i;

      return std::bind(b, i); 
    }
  };

  template<>
  struct sdbus_type_sig<const std::string &>
  {
    static const std::string sig(void) {
      return "s"; 
    }

    template <typename bindtype>
    static void bind(bindtype b, sdbus::MethodCall call)
    {
      std::string s;

      call >> s;

      return std::bind(b, s); 
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

  
  struct sdbus_wrapper_base
  {
    virtual const std::string arg_sig() = 0;
    virtual const std::string ret_sig() = 0;
    
    virtual void invoke(sdbus::MethodCall) = 0;
  };
  
  template <class C, typename R, typename... A>
  struct sdbus_wrapper : public sdbus_wrapper_base
  {
    C *obj;
    R (C::*f)(A...);
    
    sdbus_wrapper(R (C::*_f)(A...), C *_obj) : f(_f), obj(_obj) {      
    }

    virtual const std::string arg_sig()
    {
      return sdbus_type_sig<A...>::sig();
    }
    
    virtual const std::string ret_sig()
    {
      return "";
    }
    
    virtual void invoke(sdbus::MethodCall call)
    {
      auto bound = std::bind(f, obj);

      auto readied = sdbus_type_sig<A...>::bind(bound, call);

      readied();
    }
  };
};
