#include <iostream>

#include <math.h>

#include <pirsamp/pirsamp.hpp>

int main(int argc, char **argv)
{
  auto trigger = sample_buffers.get_trigger();

  auto adc0 = sample_buffers.get_adc(0);

  int n = adc0->get_size() / 2;

  volatile uint32_t *p = (volatile uint32_t *)adc0->get_buffer_addr();

  std::cout << std::hex;

  std::cout << "Buffer contents: " << n << std::endl;
  
  for (int i = 0; i < n/2; i++) {
    std::cout << *p++ << std::endl;
  }

  std::cout << std::dec;
}
