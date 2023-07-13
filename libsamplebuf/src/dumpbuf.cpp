#include <iostream>
#include <fmt/core.h>

#include <piradio/samplebuf.hpp>

int main(int argc, char **argv)
{
  piradio::sample_buffer tb(piradio::sample_buffer::OUT, 0);

  auto v = tb.get_view<piradio::complex_sample>();

  std::cout << "Number of Samples: " << v.nsamples() << std::endl;

  
  for (int i = 0; i < v.nsamples(); i++) {
    
    
    std::cout << fmt::format("{:04x} {:04x}", (uint32_t)v[i].re, (uint32_t)v[i].im) << std::endl;
  }
}
