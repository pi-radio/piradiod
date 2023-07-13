#pragma once

#include <filesystem>
#include <string>
#include <cmath>
#include <stdint.h>

namespace piradio
{
  class uio_map
  {
    uint32_t _map_no;
    uint64_t _addr;
    uint64_t _offset;
    uint64_t _size;
    int fd;

    void *_buffer;

    std::filesystem::path dir_entry;
    
  public:
    uio_map(const std::filesystem::path &map_entry_path, int dev_fd);
    ~uio_map();
    
    uint32_t map_no(void) { return _map_no; }
    uint64_t addr(void) { return _addr; }
    uint64_t offset(void) { return _offset; }
    uint64_t size(void) { return _size; }

    template <class T> T *buffer(void) { return reinterpret_cast<T*>(_buffer); }
  };

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
  } __attribute__((packed, aligned(4)));
  

  static inline uint16_t double_to_sample(double d)
  {
    return (uint16_t)(int16_t)(d * ((1 << 15) - 1));
  }
  
  struct real_sample {
    uint16_t v;

    real_sample(uint16_t _v) : v(_v) {};

    static real_sample zero() { return real_sample(0); }
    static real_sample one() { return real_sample(0x7FFF); }
    
    static real_sample sin(double phase) { return real_sample(double_to_sample(std::sin(phase))); }
  } __attribute__((packed, aligned(2)));

  struct complex_sample {
    uint16_t im;
    uint16_t re;

    complex_sample(uint16_t _re, uint16_t _im) : re(_re), im(_im) {}; 

    static complex_sample zero() { return complex_sample(0, 0); }
    static complex_sample one() { return complex_sample(0x7FFF, 0); }
    
    static complex_sample sin(double phase) { return complex_sample(double_to_sample(std::sin(phase)), double_to_sample(-std::cos(phase))); }
  } __attribute__((packed, aligned(4)));
  


  class sample_buffer
  {
  public:
    typedef enum {
      IN = 0,
      OUT = 1
    } direction_e;
      
    
    sample_buffer(direction_e _direction, int _n);


    size_t nbytes() { return csr->size_bytes; }

    template <class T>
    T *raw_data() { return maps[1]->buffer<T>(); }
        
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
    int fd;
    std::filesystem::path sysfs_path;
    
    volatile uint32_t *reg_buf;
    volatile uint16_t *data_buf;

    uio_map *maps[2];

    sample_buffer_csr *csr;
    
    std::string get_uio_name();
  };
};
