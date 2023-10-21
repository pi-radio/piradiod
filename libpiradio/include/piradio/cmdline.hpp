#pragma once

#include <thread>
#include <queue>
#include <map>
#include <mutex>
#include <future>
#include <memory>
#include <string>
#include <iostream>
#include <fstream>
#include <condition_variable>
#include <filesystem>
#include <cassert>
#include <functional>
#include <optional>

namespace piradio
{
  namespace CLI
  {
    class OptionBase
    {
    public:
    protected:
    };

    class ArgumentBase
    {
    public:
    protected:
    };
    
    typedef std::queue<std::string> args_t;
    
    template <typename T>
    class Option
    {
    public:
    protected:
    };

    template <typename T>
    class Argument
    {
    public:
    protected:
    };

    template <typename T>
    class ArgumentDesc
    {
    public:
      
    };

    
    class too_few_arguments : public std::exception
    {
    };

    template <typename T>
    class ValueWrapper
    {
    public:
      T v;
      
      ValueWrapper(args_t &inargs)
      {
	if (!inargs.size()) {
	  throw too_few_arguments();
	}
      
	std::string s = inargs.front();
	inargs.pop();

	v = T(s);
      }
      
      operator T() { return v; }
    };

    template<>
    ValueWrapper<args_t &>::ValueWrapper(args_t &inargs);    
    
    template<typename... args>
    int parse_argument_values(std::function<int (args...)> f, args_t &inargs) {
      return f(ValueWrapper<args>(inargs)...);
    }

    class CommandBase
    {
    public:
      virtual int _parse(args_t &) = 0;

      int parse(int argc, const char **argv) {
	args_t inargs;

	for (int i = 0; i < argc; i++) {
	  inargs.push(argv[i]);
	}

	return _parse(inargs);
      }

      virtual int operator()(args_t &args) = 0;
    };

    template <typename... Ts>
    class Command : public CommandBase
    {
      template<typename T> friend T fetch_argument(args_t &);
      template<typename... args> friend int parse_argument_values(std::function<int (args...)> f, args_t &inargs);
    public:
      Command() : _name(""), _f(nullptr)
      {
      }
      
      Command(const std::string &name, std::function<int (Ts...)> f) : _name(name), _f(f)
      {
      }
    
      int operator()(args_t &inargs)
      {
	return _parse(inargs);
      }

      template <typename... TTs>
      Command<TTs...> &add_command(const std::string &command, int (*f)(TTs...)) {
	assert(arguments.size() == 0);

	Command<TTs...> *retval = new Command<TTs...>(command, std::function<int (TTs...)>(f));

	subcommands[command] = retval;

	return *retval;
      }
      
      void usage() {
	std::cerr << invocation_name << " <command>" << std::endl;

	for (auto it: subcommands) {
	  std::cerr << " " << it.first << std::endl;
	}
      }
      
      int _parse(args_t &inargs) {
	invocation_name = inargs.front();
    
	inargs.pop();

	// Consume options
	while(inargs.size() && inargs.front()[0] == '-') {
	  auto opt = inargs.front();
	  inargs.pop();
	  
	  std::cerr << "Parsing option " << opt << std::endl;
	}

	if (subcommands.size()) {
	  if (inargs.size() == 0) {
	    std::cerr << "No command given" << std::endl;
	    usage();
	    return 1;
	  }

	  subcommand = inargs.front();

	  if (!subcommands.contains(subcommand)) {
	    std::cerr << "Unknown command: " << subcommand << std::endl;
	    usage();
	    return 1;
	  }

	  // If allowing chained commands, don't just return
	  return (*subcommands[subcommand])(inargs);
	} else {
	  try {
	    return parse_argument_values(_f, inargs);
	  } catch(too_few_arguments) {
	    std::cerr << "Too few arguments for command " << invocation_name << std::endl;
	    usage();
	    return 1;
	  }
	}
      }
      
    protected:
      std::map<std::string, CommandBase *> subcommands;
      std::map<std::string, OptionBase> options;
      std::vector<ArgumentBase> arguments;
      std::string invocation_name;
      std::string subcommand;
      std::map<std::string, std::string> option_values;

      std::string _name;
      std::function<int (Ts...)> _f;
    };

    class CLI : public Command<>
    {
    public:

    protected:
    };
    
  };
};
