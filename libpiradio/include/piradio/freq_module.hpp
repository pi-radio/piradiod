#pragma once

#include <functional>

#include <piradio/frequency.hpp>
#include <piradio/nrange.hpp>

namespace piradio
{
  struct freq_source;

  struct freq_sink
  {
    const freq_source *prev;

    freq_sink();

    void connect_sink(freq_source *_prev);
    
    frequency input_frequency(void) const;

    std::function<void(void)> update_sink;
  };

  struct freq_source
  {
    const freq_sink *next;

    std::function<frequency(void)> output_frequency;

    //freq_source();
    freq_source(std::function<frequency(void)> _freq);

    void update_source(void);
  };

  struct freq_mod : public freq_sink, freq_source
  {
    freq_mod(freq_source &_prev);
    freq_mod(freq_mod &_mod);
    
    std::function<frequency(frequency)> compute;

    frequency do_compute(void) const;
  };

  
};
