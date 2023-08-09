#include <iostream>
#include <cstring>

#include <signal.h>

#include <piradio/daemon.hpp>

namespace piradio
{
  int daemon_instances = 0;
  
  daemon::daemon(const std::string &_service_name) : service_name(_service_name)
  {
    std::cout << "uid: " << getuid() << std::endl;
    std::cout << "Creating connection for bus "<< service_name <<  std::endl;
    sdbus_conn = sdbus::createSystemBusConnection(service_name);
    
    sd_journal_print(LOG_INFO, "daemon created");
    
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

  dbus::obj daemon::create_sdbus_object(const std::string &name)
  {
    obj_map.emplace(name, sdbus::createObject(*sdbus_conn, name));
    
    return std::make_tuple(name);
  }

  dbus::iface daemon::create_sdbus_iface(dbus::obj &obj, const std::string &name)
  {
    return std::make_tuple(std::get<0>(obj), name);
  }

  
  void daemon::invoke_sdbus_wrapper(dbus::wrapper_base *wrapper, sdbus::MethodCall call)
  {
    try {
      wrapper->invoke(call);
    } catch(const std::runtime_error &e) {
      throw sdbus::Error(service_name, e.what());
    }
  }

  
  void daemon::register_sdbus_method(dbus::iface &iface,
				     const std::string &name, const std::string &insig,
				     const std::string &retsig, std::function<void(sdbus::MethodCall) > f)
  {
    obj_map[std::get<0>(iface)]->registerMethod(std::get<1>(iface), name, insig, retsig, f);
  }

  void daemon::register_sdbus_signal(dbus::iface &iface,
				     const std::string &name, const std::string &insig)
  {
    obj_map[std::get<0>(iface)]->registerSignal(std::get<1>(iface), name, insig);
  }

  
  void daemon::finalize_sdbus_object(dbus::obj &obj)
  {
    obj_map[std::get<0>(obj)]->finishRegistration();
  }
  
  void daemon::launch(void)
  {
    int result;

    sdbus_conn->enterEventLoopAsync();
    
    result = prepare();

    if (result != 0) {
      std::cerr << "prepare failed: " << std::strerror(result) << std::endl;
      return_promise.set_value(result);
      throw std::runtime_error("Unable to prepare daemon");
    }
    
    sd_notify("READY=1");

    int dresult = service_loop();

    sd_notify("STOPPING=1");
    
    result = cleanup();

    if (result != 0) {
      std::cerr << "cleanup failed: " << std::strerror(result) << std::endl;
      // sd_notify??
      if (dresult == 0) {
	dresult = result;
      }
    }

    sd_notify(fmt::format("EXIT_STATUS={:d}", dresult));
    
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

  int daemon::service_loop(void) {
    while(true) {
      std::shared_ptr<piradio::daemon_event> event = wait_event();

      if (event->is_a<piradio::daemon_reload_event>()) {
	continue;
      } else if (event->is_a<piradio::daemon_shutdown_event>()) {
	break;
      }
    }

    return 0;
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
	recv_sig = SIGINT;
      }

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
