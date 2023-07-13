#include <iostream>
#include <vector>
#include <map>

#include <grpc/grpc.h>
#include <grpcpp/security/server_credentials.h>
#include <grpcpp/server.h>
#include <grpcpp/server_builder.h>
#include <grpcpp/server_context.h>

#include <piradio/samplebuf.hpp>

#include "sampled.grpc.pb.h"

class sampled final : public PiRadioSampled::Service
{
  std::map<int, piradio::sample_buffer *> adc_buffers;
  std::map<int, piradio::sample_buffer *> dac_buffers;
  
public:
  sampled();

  int n_adc_buffers() { return adc_buffers.size(); }
  int n_dac_buffers() { return dac_buffers.size(); }

  virtual grpc::Status GetSampledInfo(grpc::ServerContext* context, const ::google::protobuf::Empty* request, ::SampledInfo* response);
  virtual grpc::Status GetSampleInfo(grpc::ServerContext* context, const ::SampleBufferInfoQuery* request, ::SampleBufferInfo* response);
  virtual grpc::Status SetSamples(grpc::ServerContext* context, const ::SampleData* request, ::SetSamplesResponse* response);
  virtual grpc::Status GetSamples(grpc::ServerContext* context, const ::GetSamplesRequest* request, ::SampleData* response);
};

sampled::sampled()
{
  int i;
  
  for (i = 0; i < 8; i++) {
    adc_buffers[i] = new piradio::sample_buffer(piradio::sample_buffer::IN, i);
  }

  for (i = 0; i < 8; i++) {
    dac_buffers[i] = new piradio::sample_buffer(piradio::sample_buffer::OUT, i);
  }
}

grpc::Status sampled::GetSampledInfo(grpc::ServerContext* context, const ::google::protobuf::Empty* request, ::SampledInfo* response)
{
  response->set_n_adc_buffers(n_adc_buffers());
  response->set_n_dac_buffers(n_dac_buffers());

  return grpc::Status::OK;
}

grpc::Status sampled::GetSampleInfo(grpc::ServerContext* context, const SampleBufferInfoQuery* request, ::SampleBufferInfo* response)
{
  piradio::sample_buffer *buffer;

  if (request->direction() == ADC) {
    if (request->buffer_no() > n_adc_buffers()) {
      return grpc::Status(grpc::StatusCode::INVALID_ARGUMENT, "Buffer number invalid");
    }
    
    response->set_nsamples(4096);
    response->set_sample_rate(2e9);
  
    return grpc::Status::OK;

  } else if(request->direction() == DAC) {
    if (request->buffer_no() > n_dac_buffers()) {
      return grpc::Status(grpc::StatusCode::INVALID_ARGUMENT, "Buffer number invalid");
    }
    response->set_nsamples(4096);
    response->set_sample_rate(2e9);
  
    return grpc::Status::OK;
  }
  
  return grpc::Status(grpc::StatusCode::INVALID_ARGUMENT, "Direction invalid");
}

grpc::Status sampled::SetSamples(grpc::ServerContext* context, const ::SampleData* request, ::SetSamplesResponse* response)
{
  return grpc::Status::OK;
}

grpc::Status sampled::GetSamples(grpc::ServerContext* context, const ::GetSamplesRequest* request, ::SampleData* response)
{
  return grpc::Status::OK;
}

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
