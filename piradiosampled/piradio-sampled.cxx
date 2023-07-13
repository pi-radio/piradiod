#include <iostream>

#include <grpc/grpc.h>
#include <grpcpp/security/server_credentials.h>
#include <grpcpp/server.h>
#include <grpcpp/server_builder.h>
#include <grpcpp/server_context.h>

#include <piradio/samplebuf.hpp>

#include "sampled.grpc.pb.h"

class sampled final : public PiRadioSampled::Service
{
};

void run_server(void)
{
  std::string server_address("0.0.0.0:7778");

  sampled service;

  grpc::ServerBuilder builder;

  builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
  builder.RegisterService(&service);
  std::unique_ptr<grpc::Server> server(builder.BuildAndStart());
  server->Wait();
}

int main(int argc, char **argv)
{
  run_server();
}
