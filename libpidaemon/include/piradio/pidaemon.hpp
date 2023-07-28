#pragma once

#include <thread>
#include <queue>
#include <mutex>
#include <future>
#include <memory>
#include <condition_variable>

#include <systemd/sd-daemon.h>

#include <sdbus-c++/sdbus-c++.h>

#include <grpc/grpc.h>
#include <grpcpp/server.h>
#include <grpcpp/server_builder.h>
#include <grpcpp/server_context.h>
#include <grpcpp/ext/proto_server_reflection_plugin.h>

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

    void start(void);

    int wait_on(void);
    int exit_code(void);

    void queue_event(daemon_event::ptr);

    daemon_event::ptr wait_event(void);

  protected:
    const std::string service_name;

    virtual void launch(void);
    virtual void sigloop(void);

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
