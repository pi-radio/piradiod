#pragma once

#include <tuple>
#include <functional>

#include <sdbus-c++/sdbus-c++.h>

namespace piradio
{
  namespace dbus
  {
    typedef std::tuple<const std::string> obj;

    typedef std::tuple<const std::string, const std::string> iface;

    struct wrapper_base
    {
      virtual void invoke(sdbus::MethodCall) = 0;
    };

    template <typename T>
    static inline char _arg_sig(void)
    {
      throw std::runtime_error(std::string("Unhandled argument type") + typeid(T).name());
    }

    template <> char _arg_sig<int>(void) { return 'i'; }
    template <> char _arg_sig<double>(void) { return 'd'; }
    template <> char _arg_sig<bool>(void) { return 'b'; }
    
    template <typename R, typename C, typename... A>
    static inline const char *arg_sig(R (C::*f)(A...))
    {
      static const char sig[] = { _arg_sig<A>()..., 0 };
      return sig;
    }

    template <typename R, typename C>
    static inline const char *arg_sig(R (C::*f)(void))
    {
      return "";
    }
    

    template <typename R, typename C, typename... A>
    static inline const char *ret_sig(R (C::*f)(A...))
    {
      static const char sig[] = { _arg_sig<R>(), 0 };
      return sig;
    }

    template <typename C, typename... A>
    static inline const char *ret_sig(void (C::*f)(A...))
    {
      return "";
    }

    
    template <typename A>
    static inline A fetch(sdbus::MethodCall &call)
    {
      A v;
      call >> v;
      return v;
    }

    template <typename T>
    struct method_call
    {
      T &proxy;
      sdbus::MethodCall call;

      method_call(T &_proxy, sdbus::MethodCall _call) : proxy(_proxy), call(_call)
      {
      }
      

      template <typename... Args>
      auto operator()(Args... args)
      {
	(call << ... << args);

	return proxy.call_method(call);
      }
    };

    struct proxy
    {
      std::unique_ptr<sdbus::IProxy> sbus_proxy;
      uint64_t timeout;
      std::string default_interface;

      proxy(void)
      {
	timeout = 10000;
      }
      
      proxy &attach(const std::string &bus, const std::string &object)
      {
        sbus_proxy = sdbus::createProxy(bus, object);
	return *this;
      }

      proxy &connect(void)
      {
	sbus_proxy->finishRegistration();
	return *this;
      }

      auto call_method(sdbus::MethodCall call)
      {
	sbus_proxy->callMethod(call, timeout);
      }
      
      method_call<proxy> call(const std::string &iface, const std::string &method)
      {
	return method_call<proxy>(*this, sbus_proxy->createMethodCall(iface, method));
      }

      method_call<proxy> call(const std::string &method)
      {
	return method_call<proxy>(*this, sbus_proxy->createMethodCall(default_interface, method));
      }
      
    };
      
    template <typename R>
    static inline void reply(sdbus::MethodReply &reply, R &r)
    {
      reply << r;
    }

    template <size_t I, typename... Rs>
    static inline void reply_tuple(sdbus::MethodReply &reply, std::tuple<Rs...> &r)
    {
      if constexpr(I == sizeof...(Rs)) return;
    
      reply << std::get<I>(r);
      reply_tuple<I+1>(reply, r);
    }


    template <typename... Rs>
    static inline void reply(sdbus::MethodReply &reply, std::tuple<Rs...> &r)
    {
      reply_tuple<0>(reply, r);
    }
  
  
    template <typename R, class C, typename... A>
    struct wrapper : public wrapper_base
    {
      R (C::*mf)(A...);
      C *obj;
      
      wrapper(R (C::*_f)(A...), C *_obj) : mf(_f), obj(_obj) // f([_f, _obj](A... args) { (_obj->*_f)(args...);  }) {      
      {
      }

      virtual void invoke(sdbus::MethodCall call)
      {
	R r = (obj->*mf)(fetch<A>(call)...);
    
	auto _reply = call.createReply();
	reply(_reply, r);
	_reply.send();
      }
    };

    template <class C, typename... A>
    struct void_wrapper : public wrapper_base
    {
      void (C::*mf)(A...);
      C *obj;
      
      void_wrapper(void (C::*_f)(A...), C *_obj) : mf(_f), obj(_obj)      
      {
      }
 
      virtual void invoke(sdbus::MethodCall call)
      {
	(obj->*mf)(fetch<A>(call)...);
    
	auto reply = call.createReply();
	reply.send();
      }
    };

    template <typename R, class C, typename... A>
    static inline wrapper_base *wrap(R (C::*_f)(A...), C *_obj)
    {
      return new wrapper(_f, _obj);
    }

    template <class C, typename... A>
    static inline wrapper_base *wrap(void (C::*_f)(A...), C *_obj)
    {
      return new void_wrapper(_f, _obj);
    }
    
    
  };
};
