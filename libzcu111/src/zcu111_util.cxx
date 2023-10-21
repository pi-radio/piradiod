#include <queue>
#include <iostream>

#include <piradio/cmdline.hpp>
#include <piradio/zcu111.hpp>

piradio::ZCU111 zcu111;

extern std::map<piradio::frequency, std::vector<unsigned> > predefined;

int init()
{
  piradio::setup_clocks();

  return 0;
}

int sample_freq(piradio::frequency f)
{
  std::cout << "Tuning sampling frequencies to " << f << std::endl;

  std::map<int, uint16_t> lmx_regs;
  piradio::LMX2594 lmx(piradio::MHz(122.88));

  lmx.tune(f, f);

  lmx.config.fill_regs(lmx_regs);


  if (predefined.contains(f)) {
    std::cout << "Checking against predefined" << std::endl;
    std::map<int, uint16_t> lmx_regs2;

    for (auto v: predefined[f]) {
      lmx_regs2[(v >> 16)] = v & 0xFFFF;
    }

    for (auto e: lmx_regs) {
      if (e.second != lmx_regs2[e.first]) {
	std::cout << "Difference: Register: " << e.first << " " << lmx_regs2[e.first] << " " << e.second << std::endl;
      }
    }
  }
  
  zcu111.i2c_program_lmx(0xD, lmx_regs);
  
  //zcu111.tune_all(f);

  return 0;
}

int write_regs(piradio::CLI::args_t &args)
{
  args.pop();
  
  piradio::frequency f(args.front());

  args.pop();

  std::cout << "Tuning to " << f << std::endl;

  std::map<int, uint16_t> lmx_regs;
  piradio::LMX2594 lmx(piradio::MHz(122.88));

  lmx.tune(f, f);

  lmx.config.fill_regs(lmx_regs);

  std::ofstream regfile("regs-cpp.txt");
    
  for (auto it = lmx_regs.crbegin(); it != lmx_regs.crend(); it++) {
    uint8_t addr = it->first;
    uint16_t r = it->second;

    regfile << "R" << std::dec << std::setw(0) << int(addr) << " 0x" <<
      std::hex << std::setfill('0') << std::setw(2) << int(addr) << std::setw(4) << r << std::endl;
  }

  return 0;
}


int main(int argc, const char **argv)
{
  piradio::CLI::CLI cli;

  cli.add_command("init", init);
  cli.add_command("sample-freq", sample_freq);
  cli.add_command("write-regs", write_regs);

  cli.parse(argc, argv);
}
