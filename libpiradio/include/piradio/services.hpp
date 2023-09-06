#pragma once

#include <piradio/dbus.hpp>

namespace piradio
{
  namespace services
  {
    namespace fpgad
    {
      static const std::string bus{"io.piradio.fpgad"};
      static const std::string root_object{"/io/piradio/fpgad/fpga"};
      static const std::string root_interface{"io.piradio.fpgad.fpga"};

      
      static inline dbus::proxy &attach_proxy(dbus::proxy &proxy)
      {
	proxy.default_interface = root_interface;
	return proxy.attach(bus, root_object);
      }
    };
    
    namespace rfdcd
    {
      static const std::string bus{"io.piradio.rfdcd"};
      static const std::string root_object{"/io/piradio/rfdcd/rfdc"};
      static const std::string root_interface{"io.piradio.rfdcd.rfdc"};

      static inline dbus::proxy &attach_proxy(dbus::proxy &proxy)
      {
	proxy.default_interface = root_interface;
	return proxy.attach(bus, root_object);
      }
    };
    
    namespace zcu111d
    {
      static const std::string bus{"io.piradio.zcu111d"};
      static const std::string root_object = "/io/piradio/zcu111d/zcu111";
      static const std::string root_interface = "io.piradio.zcu111d.zcu111";

      static inline dbus::proxy &attach_proxy(dbus::proxy &proxy)
      {
	proxy.default_interface = root_interface;
	return proxy.attach(bus, root_object);
      }
    };

    namespace sampled
    {
      static const std::string bus{"io.piradio.sampled"};
      static const std::string root_object = "/io/piradio/sampled";
      static const std::string root_interface = "io.piradio.sampled";
      
      static inline dbus::proxy &attach_proxy(dbus::proxy &proxy)
      {
	proxy.default_interface = root_interface;
	return proxy.attach(bus, root_object);
      }
    };
    
  };
};
