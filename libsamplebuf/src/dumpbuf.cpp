#include <iostream>
#include <fmt/core.h>

#include <piradio/samplebuf.hpp>

int main(int argc, char **argv)
{
  piradio::sample_buffer<piradio::complex_sample> tb(piradio::sample_buffer_base::OUT, 0);

  std::cout << "Number of Samples: " << tb.nsamples() << std::endl;
  
  for (int i = 0; i < tb.nsamples(); i++) {
    
    
    std::cout << fmt::format("{:04x} {:04x}", (uint32_t)tb[i].re, (uint32_t)tb[i].im) << std::endl;
  }
}
