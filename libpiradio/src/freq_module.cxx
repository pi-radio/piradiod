#include <iostream>
#include <cassert>

#include <piradio/freq_module.hpp>

namespace piradio
{
  freq_sink::freq_sink() : prev(nullptr),
			   update_sink([]() {})
  {
  }

  void freq_sink::connect_sink(freq_source *_prev)
  {
    assert(prev == nullptr);
    prev = _prev;
    if (_prev) _prev->next = this;
  }
  

  frequency freq_sink::input_frequency(void) const
  {
    return prev->output_frequency();
  }
  
  freq_source::freq_source(std::function<frequency(void)> _freq) : output_frequency(_freq)
  {
  }

  void freq_source::update_source(void)
  {
    next->update_sink();
  }

  frequency freq_mod::do_compute(void) const
  {
    frequency inf = input_frequency();
    frequency outf = compute(inf);

    return outf;
  }

  freq_mod::freq_mod(freq_mod &_mod) : freq_sink(),
				       freq_source([this](void) { return do_compute(); })
  {
    connect_sink(&_mod);
  }

  
  freq_mod::freq_mod(freq_source &_prev) : freq_sink(),
						 freq_source([this](void) { return do_compute(); })
  {
    connect_sink(&_prev);
  }
}
