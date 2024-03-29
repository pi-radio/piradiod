#pragma once

#include <filesystem>
#include <string>
#include <cmath>
#include <iostream>
#include <stdint.h>

#include <piradio/uio.hpp>

namespace piradio
{
  struct sample_buffer_csr
  {
    volatile uint32_t ip_id;
    volatile uint32_t ctrl_stat;
    volatile uint32_t start_offset;
    volatile uint32_t end_offset;
    volatile uint32_t stream_depth;
    volatile uint32_t size_bytes;
    volatile uint32_t trigger_count;
    volatile uint32_t write_count;
    volatile uint32_t wrap_count;
  } __attribute__((packed, aligned(4)));
  

  static inline uint16_t double_to_sample(double d)
  {
    return (uint16_t)(int16_t)(d * ((1 << 15) - 1));
  }
  
  struct real_sample {
    int16_t v;

    real_sample(uint16_t _v) : v(_v) {};

    static real_sample zero() { return real_sample(0); }
    static real_sample one() { return real_sample(0x7FFF); }
    
    static real_sample sin(double phase) { return real_sample(double_to_sample(std::sin(phase))); }
  } __attribute__((packed, aligned(2)));

  struct complex_sample {
    int16_t re;
    int16_t im;

    complex_sample(uint16_t _re, uint16_t _im) : re(_re), im(_im) {}; 

    static complex_sample zero() { return complex_sample(0, 0); }
    static complex_sample one() { return complex_sample(0x7FFF, 0); }
    
    static complex_sample sin(double phase) { return complex_sample(double_to_sample(std::sin(phase)), double_to_sample(-std::cos(phase))); }
  } __attribute__((packed, aligned(4)));
  


  class sample_buffer : public uio_device
  {
    std::filesystem::path get_sysfs_path(int _dir, int _n);

  public:
    typedef enum {
      IN = 0,
      OUT = 1
    } direction_e;
      
    sample_buffer(direction_e _direction, int _n);

    bool get_one_shot(void) { return csr->ctrl_stat & 2; }
    void set_one_shot(bool v = true) {
      if (v) {
	csr->ctrl_stat = (csr->ctrl_stat & ~0x1) | 0x2;
      } else {
	csr->ctrl_stat = (csr->ctrl_stat & ~0x3);
      }
    };

    bool get_active(void) { return (csr->ctrl_stat & 1) != 0; }
    uint32_t get_ctrl_stat(void) { return csr->ctrl_stat; }

    bool get_i_en(void) { return (csr->ctrl_stat & 0x20) != 0; }

    void set_i_en(bool v) {
      if (v) {
	csr->ctrl_stat = (csr->ctrl_stat & ~0x1) | 0x20;
      } else {
	csr->ctrl_stat = (csr->ctrl_stat & ~0x21);
      }
    }
    
    bool get_q_en(void) { return (csr->ctrl_stat & 0x10) != 0; }
    
    void set_q_en(bool v) {
      if (v) {
	csr->ctrl_stat = (csr->ctrl_stat & ~0x1) | 0x10;
      } else {
	csr->ctrl_stat = (csr->ctrl_stat & ~0x11);
      }
    }

    void clear_iq() {
      csr->ctrl_stat = (csr->ctrl_stat & ~0x31);
    }
    
    uint32_t get_trigger_count(void) { return csr->trigger_count; }
    uint32_t get_write_count(void) { return csr->write_count; }

    uint32_t get_wrap_count(void) { return csr->wrap_count; }
    
    size_t nbytes() { return csr->size_bytes; }

    template <class T>
    T *raw_data() { return get_map(1)->buffer<T>(); }
        
    template <class _sample_type>
    class view
    {
    public:
      using sample_type = _sample_type;
      sample_buffer &buffer;
    
      view(sample_buffer &_buffer) : buffer(_buffer) {};

      size_t nsamples() { return buffer.nbytes() / sizeof(sample_type); }

      sample_type &operator[](off_t n)
      {
	return buffer.raw_data<sample_type>()[n];
      }

      
    };
    
    template <class sample_type>
    view<sample_type> get_view()
    {
      return view<sample_type>(*this);
    };
    
  protected:
    direction_e direction;
    int n;
    
    volatile uint32_t *reg_buf;
    volatile uint16_t *data_buf;

    sample_buffer_csr *csr;
    
    std::string get_uio_name();
  };
};
