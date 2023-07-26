#pragma once

#include <filesystem>
#include <string>
#include <cmath>
#include <stdint.h>

#include <piradio/uio.hpp>

namespace piradio
{
  struct trigger_csr
  {
    volatile uint32_t ip_id;
    volatile uint32_t enables;
    volatile uint32_t trigger;
    volatile uint32_t delay[32];
  } __attribute__((aligned(4), packed));

  class trigger : public uio_device
  {
    std::filesystem::path get_sysfs_path(void);

    struct trigger_csr *csr;
    
  public:
    trigger();

    void enable_channel(int n) { csr->enables = csr->enables | (1 << n); }
    void disable_channel(int n) { csr->enables = csr->enables & ~(1 << n); }

    void activate(void) { csr->trigger = 0xFFFFFFFF; }

    int get_delay(int n) { return csr->delay[n]; }
    void set_delay(int n, int cycles) { csr->delay[n] = cycles; }
  };
};
