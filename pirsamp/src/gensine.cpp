#include <iostream>

#include <math.h>

#include <pirsamp/pirsamp.hpp>

void real_sine(int16_t *buf, int n)
{
  double N = 4000;
  double sample_rate = 4e9;
  double t = n / sample_rate;
  double theta = 0.0;
  double dtheta = N * 2 * M_PI / n;

  std::cout << "n: " << n << std::endl;
  std::cout << "t: " << t * 1e9 << " ns" << std::endl;
  std::cout << "f: " << N / t /1e6 << " MHz" <<  std::endl;
  
  for (int i = 0; i < n; i++) {
    double v = (1 << 15) * sin(theta);
    
    *buf++ = v;

    theta += dtheta;
  }
}


int main(int argc, char **argv)
{
  auto trigger = sample_buffers.get_trigger();

  auto adc0 = sample_buffers.get_adc(0);
  auto dac0 = sample_buffers.get_dac(0);

  auto dac_buf = dac0->get_buffer_addr();

  int n = dac0->get_size() / 2;
  
  auto b = new int16_t[n];

  real_sine(b, n);

  auto p32 = dac_buf;
  int16_t *p16 = b;

  std::cout << "Writing to device RAM" << std::endl;
  
  for (int i = 0; i < n/2; i++) {
    uint32_t v = ((uint32_t)*p16++ << 16) | *p16++;
    *p32++ = v;
  }

  p32 = dac_buf;

#if 0
  for (int i = 0; i < n/2; i++) {
    std::cout << *p32++ << std::endl;
  }
#endif
  
  trigger->trigger();
}
