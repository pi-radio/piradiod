#pragma once

#include <sstream>

#include <systemd/sd-journal.h>

namespace sdjournal
{
  template <int n>
  struct priority
  {
  };

  const priority<LOG_INFO> info;
  const priority<LOG_ERR> error;

  template <int p>
  class entry : public std::stringstream
  {
  public:
    entry(const priority<p> &_p) {    
    }

    ~entry() {
      sd_journal_print(p, str().c_str());
    }
  };
}
