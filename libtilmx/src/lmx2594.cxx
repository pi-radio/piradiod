#include <vector>
#include <cmath>
#include <stdexcept>
#include <map>
#include <functional>
#include <iostream>

#include <piradio/frequency.hpp>
#include <piradio/nrange.hpp>
#include <piradio/lmx2594_config.hpp>

namespace piradio
{
  class InternalVCO
  {
    int sel;
    frequency_range fr;
    nrange gain;
    nrange amp_cal;
    nrange cap_ctrl;
  
  public:
    InternalVCO(int _sel,
		const frequency_range &_fr,
		const nrange &_gain,
		const nrange &_amp_cal,
		const nrange &_cap_ctrl) : sel(_sel),
					   fr(_fr),
					   gain(_gain),
					   amp_cal(_amp_cal),
					   cap_ctrl(_cap_ctrl)
    {      
    }


  
    int get_sel() { return sel; }
    int get_gain(const frequency &f) { return gain.lerp(fr.bc(f)); }
    int get_amp_cal(const frequency &f) { return gain.lerp(fr.bc(f)); }
    int get_cap_ctrl(const frequency &f) { return gain.lerp(fr.bc(f)); }
  };

  std::vector<InternalVCO> LMX2594_VCO{
    { 1, { MHz(7500), MHz(8600) }, {73, 114 },  { 299, 240 }, { 164, 12 } },
    { 2, { MHz(8600), MHz(9800) }, { 61, 121 }, { 356, 247 }, { 165, 16 } },
    { 3, { MHz(9800), MHz(10800) }, { 98, 132 }, { 324, 224 }, { 158, 19 } },
    { 4, { MHz(10800), MHz(12000) }, { 106, 141 },  { 383, 244 }, { 140, 0} },
    // Frequency Hole
    { 4, { MHz(11900), MHz(12100) }, { -1, -1 },  { 100, 100 }, { 0, 0 } },
    { 5, { MHz(12000), MHz(12900) }, { 170, 215 },  { 205, 146 }, { 183, 36 } },
    { 6, { MHz(12900), MHz(13900) }, { 172, 218 }, { 242, 163 }, { 155, 6 } },
    { 7, { MHz(13900), MHz(15000) }, { 182, 239 }, { 323, 244 }, { 175, 19 } }
  };

  template<class...Ts>
  struct sink : std::function<void(Ts...)> {
    using std::function<void(Ts...)>::function;
  };

  template<class...Ts>
  using source = sink<sink<Ts...>>;

  template<class In, class Out>
  using process = sink< source<In>, sink<Out> >;

  template<class In, class Out>
  sink<In> operator|( process< In, Out > a, sink< Out > b ){
    return [a,b]( In in ){
      a( [&in]( sink<In> s )mutable{ s(std::forward<In>(in)); }, b );
    };
  }
  template<class In, class Out>
  source<Out> operator|( source< In > a, process< In, Out > b ){
    return [a,b]( sink<Out> out ){
      b( a, out );
    };
  }

  template<class In, class Mid, class Out>
  process<In, Out> operator|( process<In, Mid> a, process<Mid, Out> b ){
    return [a,b]( source<In> in, sink<Out> out ){
      a( in, b|out ); // or b( in|a, out )
    };
  }
  template<class...Ts>
  sink<> operator|( source<Ts...> a, sink<Ts...> b ){
    return[a,b]{ a(b); };
  }

  process<char, char> to_upper = []( source<char> in, sink<char> out ){
    in( [&out]( char c ) { out( std::toupper(c) ); } );
  };

  source<char> hello_world = [ptr="hello world"]( sink<char> s ){
    for (auto it = ptr; *it; ++it ){ s(*it); }
  };
  sink<char> print = [](char c){std::cout<<c;};

  int example(){
    auto prog = hello_world|to_upper|print;
    prog();
    return 0;
  }

  struct freq_source;

  struct freq_sink
  {
    freq_source &prev;

    freq_sink(freq_source &_prev);

    std::function<void(void)> update_sink;
  };

  struct freq_source
  {
    freq_sink *next;

    std::function<frequency(void)> freq;

    //freq_source();
    freq_source(std::function<frequency(void)> _freq);

    void update_source(void);
  };

  struct freq_mod : public freq_sink, freq_source
  {
    freq_mod(freq_source &_prev);

    std::function<frequency(frequency)> compute;
  };

  freq_sink::freq_sink(freq_source &_prev) : prev(_prev),
					     update_sink([]() {})
  {
    prev.next = this;
  }

  freq_source::freq_source(std::function<frequency(void)> _freq) : freq(_freq)
  {
  
  }

  void freq_source::update_source(void)
  {
    next->update_sink();
  }

  freq_mod::freq_mod(freq_source &_prev) : freq_sink(_prev),
					   freq_source([this](void) { return compute(prev.freq()); })
  {
  }
  
  class LMX2594
  {
  public:
    freq_source  osc_in;
    frequency    _osc_in;
  
    freq_mod     osc_2x;
    bool         _doubler_en;
  
    freq_mod     osc_pre_div;
    int          _pre_div;
  
    freq_mod     osc_mult;
    int          _osc_mult;

    freq_mod     osc_post_div;
    int          _post_div;

    double       _fpd;

    int          _pll_N;
  
    LMX2594(const frequency &_f_osc_in) : osc_in([this](void) { return _osc_in; }),
					  osc_2x(osc_in),
					  osc_pre_div(osc_2x),
					  osc_mult(osc_pre_div),
					  osc_post_div(osc_mult)
    {
      osc_2x.compute = [this](frequency f) { return _doubler_en ? 2*f : f; };
      osc_pre_div.compute = [this](frequency f) { return f / _pre_div; };
      osc_mult.compute = [this](frequency f) { return f * _osc_mult; };
      osc_post_div.compute = [this](frequency f) { return f / _post_div; };
    }

    void validate(void)
    {
      if (_osc_in.MHz() < 5.0) throw std::runtime_error("Minimum frequency for OSC_IN is 5.0MHz");
      if (_osc_in.MHz() > 1400.0) throw std::runtime_error("Maximum frequency for OSC_IN is 1400.0MHz");

      if (_doubler_en && _osc_in.MHz() > 700.0) throw std::runtime_error("Maximum frequency for OSC_IN doubler is 1400.0MHz");

      if (_osc_mult == 2) throw std::runtime_error("Pre-mult of 2 not supported");
    
    }
  
    void set_osc_in(const frequency &f)
    {
      _osc_in = f;
      validate();
    }

    void set_doubler_en(bool b)
    {
      _doubler_en = b;
    }
  
  protected:
  };

};
