#pragma once

#include <thread>
#include <queue>
#include <map>
#include <mutex>
#include <future>
#include <memory>
#include <string>
#include <fstream>
#include <condition_variable>
#include <filesystem>

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include <fmt/core.h>

#include <systemd/sd-daemon.h>
#include <systemd/sd-journal.h>


#include <grpc/grpc.h>
#include <grpcpp/server.h>
#include <grpcpp/server_builder.h>
#include <grpcpp/server_context.h>
#include <grpcpp/ext/proto_server_reflection_plugin.h>

#include <piradio/dbus.hpp>

namespace piradio
{
  class runfile : public std::fstream
  {
  public:
    runfile(const std::filesystem::path &path) {
      int fd = ::open(path.c_str(), O_RDWR | O_CREAT, 0644);

      if (fd < 0) {
	throw std::runtime_error(std::string("Unable to open ") + path.string());
      }
      
      open(path);
      ::close(fd);
    }
  };

  class daemon_event
  {
  public:
    virtual ~daemon_event() = default;
    
    template<class T> bool is_a()
    {
      return (dynamic_cast<T*>(this) != nullptr);
    }

    typedef std::shared_ptr<daemon_event> ptr;
  };

  class daemon_reload_event : public daemon_event
  {
  public:
  };

  class daemon_shutdown_event : public daemon_event
  {
  public:
  };

  
  class daemon
  {
  public:
    daemon(const std::string &_service_name);

    virtual int prepare(void) { return 0; };
    virtual int service_loop(void);
    virtual int cleanup(void) { return 0; };
    virtual int reload(void) { return 0; };
    
    dbus::obj create_sdbus_object(const std::string &name);
    
    dbus::iface create_sdbus_iface(dbus::obj &obj, const std::string &name);
    
    void register_sdbus_method(dbus::iface &,
			       const std::string &name, const std::string &insig,
			       const std::string &retsig, std::function<void(sdbus::MethodCall) > f);

    void invoke_sdbus_wrapper(dbus::wrapper_base *wrapper, sdbus::MethodCall);
    
    template <class C, typename R, typename... A>
    void register_sdbus_method(dbus::iface &iface,
			       const std::string &name, R (C::*f)(A...))
    {
      auto wrapper = dbus::wrap(f, dynamic_cast<C*>(this));

      register_sdbus_method(iface, name,
			    dbus::arg_sig(f), dbus::ret_sig(f),
			    [this, wrapper](sdbus::MethodCall call) { invoke_sdbus_wrapper(wrapper, call); });

      wrappers.push_back(wrapper);
    }
    
    void register_sdbus_signal(dbus::iface &iface,
			       const std::string &name, const std::string &sig);
    
    void finalize_sdbus_object(dbus::obj &);
    
    auto sd_notify(const std::string &s) {
      ::sd_notify(0, s.c_str());
    }
    
    void start(void);

    int wait_on(void);
    int exit_code(void);

    void queue_event(daemon_event::ptr);

    daemon_event::ptr wait_event(void);

  protected:
    const std::string service_name;

    std::unique_ptr<sdbus::IConnection> sdbus_conn;
    
    virtual void launch(void);
    virtual void sigloop(void);

    std::map<std::string, std::unique_ptr<sdbus::IObject> > obj_map;
    
    std::mutex daemon_event_mutex;
    std::condition_variable daemon_event_cv;
    std::queue<daemon_event::ptr> daemon_event_queue;
    
    std::thread service_thread;
    std::thread signal_thread;
    std::promise<int> return_promise;

    std::vector<dbus::wrapper_base *> wrappers;
  };

  class grpc_daemon : public daemon
  {
  public:
    grpc_daemon(const std::string &_service_name);

  protected:
    virtual void launch(void);

    void build_grpc_services(void);

    std::vector<std::string> bind_addresses;
    std::vector<grpc::Service *> grpc_services;
    std::unique_ptr<grpc::Server> grpc_server;
  };
};
