#pragma once

#include <thread>
#include <queue>
#include <map>
#include <mutex>
#include <future>
#include <memory>
#include <string>
#include <condition_variable>

#include <fmt/core.h>

#include <systemd/sd-daemon.h>
#include <systemd/sd-journal.h>

#include <sdbus-c++/sdbus-c++.h>

#include <grpc/grpc.h>
#include <grpcpp/server.h>
#include <grpcpp/server_builder.h>
#include <grpcpp/server_context.h>
#include <grpcpp/ext/proto_server_reflection_plugin.h>

#include <piradio/sdsig.hpp>

namespace piradio
{
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

    void create_sdbus_object(const std::string &str);

    void register_sdbus_method(const std::string &obj, const std::string &iface,
			       const std::string &name, const std::string &insig,
			       const std::string &retsig, std::function<void(sdbus::MethodCall) > f);

    template <typename R, typename... A>
    void register_sdbus_method(const std::string &obj, const std::string &iface,
			       const std::string &name, std::function<R(A...)> f)
    {
      
    }
    
    void register_sdbus_signal(const std::string &obj, const std::string &iface,
			       const std::string &name, const std::string &sig);
    
    void finalize_sdbus_object(const std::string &str);
    
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

    std::map<std::string, std::unique_ptr<sdbus::IObject> > sdbus_obj;
    
    std::mutex daemon_event_mutex;
    std::condition_variable daemon_event_cv;
    std::queue<daemon_event::ptr> daemon_event_queue;
    
    std::thread service_thread;
    std::thread signal_thread;
    std::promise<int> return_promise;
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
