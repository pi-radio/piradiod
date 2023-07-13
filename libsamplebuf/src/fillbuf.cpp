#include <iostream>
#include <fmt/core.h>
#include <math.h>

#include <boost/program_options.hpp>

#include <piradio/samplebuf.hpp>

namespace po = boost::program_options;

template <class sample_type>
void fill_samples(piradio::sample_buffer::view<sample_type> &buffer, const sample_type &val)
{
  for (int i = 0; i < buffer.nsamples(); i++) {
    buffer[i] = val;
  }
}

template <class sample_type>
void fill_sine(piradio::sample_buffer::view<sample_type> &buffer)
{
  double freq = 100e6;
  double sample_rate = 2e9;
  double phase_inc = 2 * M_PI * freq / sample_rate;

  double phase = 0.0;

  for(int i = 0; i < buffer.nsamples(); i++) {
    buffer[i] = sample_type::sin(phase);
    phase += phase_inc;
  }
}


template <class sample_type>
int parse_for_format(po::variables_map &vm, po::parsed_options &parsed)
{  
  piradio::sample_buffer buffer(piradio::sample_buffer::OUT, vm["buffer_number"].as<int>());

  auto view = buffer.get_view<sample_type>();
  
  std::string fill_type = vm["fill_type"].as<std::string>();

  std::cout << "Fill Type: " << fill_type  << std::endl;

  if (fill_type == "zeros") {
    fill_samples(view, sample_type::zero());
    return 0;
  } else if (fill_type == "ones") {
    fill_samples(view, sample_type::one());
    return 0;
  } else if(fill_type == "sine") {
    fill_sine(view);
    return 0;
  }

  std::cerr << "Unknwnown Fill Type: " << fill_type << std::endl;
  
  return 1;
}


int main(int argc, char **argv)
{
  po::options_description desc("Allowed options");
  desc.add_options()
    ("help", "produce help message")
    ("direction", po::value<std::string>()->default_value("out") , "direction of the buffer to fill")
    ("format", po::value<std::string>()->default_value("complex") , "direction of the buffer to fill")
    ("buffer_number", po::value<int>(), "buffer number to fill")
    ("fill_type", po::value<std::string>(), "type of fill to use")
    ;
  
  po::positional_options_description p;

  p.add("buffer_number", 1);
  p.add("fill_type", 1);

  po::variables_map vm;

  po::parsed_options parsed = po::command_line_parser(argc, argv)
    .options(desc)
    .positional(p)
    .allow_unregistered()
    .run();
  
  po::store(parsed, vm);
  po::notify(vm);

  if (vm.count("help")) {
    std::cout << desc << std::endl;
    return 1;
  }

  if (vm["format"].as<std::string>() == "complex") {
    return parse_for_format<piradio::complex_sample>(vm, parsed);
  } else if (vm["format"].as<std::string>() == "real") {
    return parse_for_format<piradio::real_sample>(vm, parsed);
  }

  std::cerr << "Unknown format " << vm["format"].as<std::string>() << std::endl;
  std::cerr << desc << std::endl;

  return 1;
}
