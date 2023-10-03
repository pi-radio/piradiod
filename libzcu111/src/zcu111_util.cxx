#include <queue>
#include <iostream>

#include <piradio/zcu111.hpp>

typedef std::queue<std::string> args_t;

piradio::ZCU111 zcu111;

typedef int (*command_handler_t)(args_t &);

class CLI
{
public:
  int add_command(const std::string &command, command_handler_t handler) {
    handlers[command] = handler;

    return 0;
  }

  int parse(int argc, const char **argv) {
    args_t args;

    for (int i = 0; i < argc; i++) {
      args.push(argv[i]);
    }

    args.pop();

    std::string command = args.front();

    command_handler_t handler;
    try {      
      handler = handlers[command];
    } catch (std::out_of_range e) {
      std::cerr << "Unknown command: " << command << std::endl;
      return 1;
    }

    return handler(args);
  }
  
protected:
  std::map<std::string, command_handler_t> handlers;
};

int init(args_t &args)
{
  args.pop();

  piradio::setup_clocks();

  return 0;
}

int sample_freq(args_t &args)
{
  args.pop();
  
  piradio::frequency f(args.front());

  args.pop();

  std::cout << "Tuning sampling frequencies to " << f << std::endl;

  zcu111.tune_all(f);

  return 0;
}

int main(int argc, const char **argv)
{
  CLI cli;

  cli.add_command("init", init);
  cli.add_command("sample-freq", sample_freq);
  
  cli.parse(argc, argv);
}
