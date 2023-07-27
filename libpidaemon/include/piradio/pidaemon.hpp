#pragma once

#include <thread>
#include <queue>
#include <mutex>
#include <future>
#include <memory>
#include <condition_variable>

#include <systemd/sd-daemon.h>

#include <sdbus-c++/sdbus-c++.h>

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
    virtual int service_loop(void) = 0;
    virtual int cleanup(void) { return 0; };
    virtual int reload(void) { return 0; };

    void start(void);

    int wait_on(void);
    int exit_code(void);

    void queue_event(daemon_event::ptr);

    daemon_event::ptr wait_event(void);

  private:
    const std::string service_name;

    void launch(void);
    void sigloop(void);

    std::mutex daemon_event_mutex;
    std::condition_variable daemon_event_cv;
    std::queue<daemon_event::ptr> daemon_event_queue;
    
    std::thread service_thread;
    std::thread signal_thread;
    std::promise<int> return_promise;
  };
};
