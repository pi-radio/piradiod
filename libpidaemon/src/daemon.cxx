#include <iostream>
#include <cstring>

#include <signal.h>

#include <piradio/pidaemon.hpp>

namespace piradio
{
  int daemon_instances = 0;
  
  daemon::daemon(const std::string &_service_name) : service_name(_service_name)
  {
    sigset_t sset;
    int result;

    assert(daemon_instances++ == 0);
    
    sigemptyset(&sset);
    sigaddset(&sset, SIGHUP);
    sigaddset(&sset, SIGTERM);
    sigaddset(&sset, SIGINT);

    result = sigprocmask(SIG_BLOCK, &sset, NULL);

    if (result != 0){
      std::cerr << "sigprocmask failed: " << std::strerror(result) << std::endl;
      throw std::runtime_error("Unable to create daemon");
    }

    
  }

  void daemon::launch(void)
  {
    int result;

    result = prepare();

    if (result != 0) {
      std::cerr << "prepare failed: " << std::strerror(result) << std::endl;
      return_promise.set_value(result);
      throw std::runtime_error("Unable to prepare daemon");
    }
    
    sd_notify(0, "READY=1");

    int dresult = service_loop();

    result = cleanup();

    if (result != 0) {
      std::cerr << "cleanup failed: " << std::strerror(result) << std::endl;
      // sd_notify??
      if (dresult == 0) {
	dresult = result;
      }
    }
    
    return_promise.set_value(dresult);
  }

  daemon_event::ptr daemon::wait_event(void)
  {
    daemon_event::ptr evt;
    
    std::unique_lock lk(daemon_event_mutex);
    daemon_event_cv.wait(lk, [this]{ return !daemon_event_queue.empty(); });
    evt = daemon_event_queue.front();
    daemon_event_queue.pop();
    lk.unlock();

    return evt;
  }

  void daemon::queue_event(daemon_event::ptr evt)
  {
    std::unique_lock lk(daemon_event_mutex);
    daemon_event_queue.push(evt);
    lk.unlock();

    daemon_event_cv.notify_one();
  }
  
  int daemon::wait_on(void)
  {
    auto f = return_promise.get_future();

    f.wait();

    service_thread.join();
    signal_thread.join();
    
    return f.get();
  }
  
  int daemon::exit_code(void)
  {
    auto f = return_promise.get_future();
    
    if (!f.valid()) {
      throw std::runtime_error("Thread not complete when asking for exit");
    }

    return f.get();
  }

  void daemon::start(void)
  {
    signal_thread = std::thread(&daemon::sigloop, this);
    
    service_thread = std::thread(&daemon::launch, this);
  }

  
  void daemon::sigloop(void)
  {
    int result;
    
    while (true) {
      int recv_sig;
      sigset_t sset;

      sigemptyset(&sset);
      sigaddset(&sset, SIGHUP);
      sigaddset(&sset, SIGTERM);
      sigaddset(&sset, SIGINT);
    
      result = sigwait(&sset, &recv_sig);

      if (result != 0) {
	std::cerr << "sigwait failed: " << std::strerror(result) << std::endl;
      }

      std::cout << "Signal: " << recv_sig << std::endl;

      if (recv_sig == SIGHUP) {
	queue_event(daemon_event::ptr(new daemon_reload_event()));
      }
      else if (recv_sig == SIGTERM) {
	queue_event(daemon_event::ptr(new daemon_shutdown_event()));
	break;
      }
      else if (recv_sig == SIGINT) {
	queue_event(daemon_event::ptr(new daemon_shutdown_event()));
	break;
      }
    }
  }
};
