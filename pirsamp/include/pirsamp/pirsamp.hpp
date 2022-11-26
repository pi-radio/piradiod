#pragma once

#include <filesystem>
#include <map>

#include <stdint.h>

class PiRadioUIOMap
{
public:
  volatile void *base;
  size_t len;

  PiRadioUIOMap(volatile void *_base = NULL, size_t _len = 0) : base(_base), len(_len) {};
  PiRadioUIOMap(std::tuple<volatile void *, size_t> t) : base(std::get<0>(t)), len(std::get<1>(t)) {};
  ~PiRadioUIOMap();
};

class PiRadioUIO
{
  int uio_fd;
  std::map<int, PiRadioUIOMap> maps;
  
public:
  // Path to a device node
  PiRadioUIO(const std::filesystem::path &);
  ~PiRadioUIO();

  template <class T> volatile T *get_map_base(int map) {
    return reinterpret_cast<volatile T*>(maps[map].base);
  }
  size_t get_map_len(int map) {
    return maps[map].len;
  }
  
};

struct PiRadioSampleBufferCSR;
struct PiRadioTriggerCSR;

class PiRadioSampleBuffer : protected PiRadioUIO
{
  volatile PiRadioSampleBufferCSR *csr;
 
public:
  PiRadioSampleBuffer(const std::filesystem::path &);

  volatile uint32_t *get_buffer_addr();
  ssize_t get_size();
};

class PiRadioSampleBufferIn : public PiRadioSampleBuffer
{
public:
  typedef std::shared_ptr<PiRadioSampleBufferIn> ptr;

  PiRadioSampleBufferIn(uint64_t base);
};

class PiRadioSampleBufferOut : public PiRadioSampleBuffer
{
public:
  typedef std::shared_ptr<PiRadioSampleBufferOut> ptr;
    
  PiRadioSampleBufferOut(uint64_t base);
};


class PiRadioTrigger : public PiRadioUIO
{
  volatile PiRadioTriggerCSR *csr;
  
public:
  typedef std::shared_ptr<PiRadioTrigger> ptr;
  
  PiRadioTrigger(uint64_t);

  void trigger(void);
};

class PiRadioSampleBuffers
{
  intptr_t trigger_addr;

  std::map<int, PiRadioSampleBufferOut::ptr> DAC_obj;
  std::map<int, PiRadioSampleBufferIn::ptr> ADC_obj;

  std::map<int, PiRadioTrigger::ptr> triggers;
  
public:
  PiRadioSampleBuffers();

  PiRadioSampleBufferIn::ptr get_adc(int);
  PiRadioSampleBufferOut::ptr get_dac(int);  
  PiRadioTrigger::ptr get_trigger();
};

extern PiRadioSampleBuffers sample_buffers;
