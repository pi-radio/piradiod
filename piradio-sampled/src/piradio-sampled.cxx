#include <iostream>
#include <vector>
#include <map>

#include <grpc/grpc.h>
#include <grpcpp/security/server_credentials.h>
#include <grpcpp/server.h>
#include <grpcpp/server_builder.h>
#include <grpcpp/server_context.h>
#include <grpcpp/ext/proto_server_reflection_plugin.h>

#include <piradio/pidaemon.hpp>
#include <piradio/samplebuf.hpp>
#include <piradio/trigger.hpp>

#include "sampled.grpc.pb.h"

class sampled final : public PiRadioSampled::Service
{
  piradio::trigger trigger;
  std::map<int, piradio::sample_buffer *> adc_buffers;
  std::map<int, piradio::sample_buffer *> dac_buffers;
  
public:
  sampled();

  int n_adc_buffers() { return adc_buffers.size(); }
  int n_dac_buffers() { return dac_buffers.size(); }

  std::tuple<grpc::Status, piradio::sample_buffer *> get_buffer(const BufferId &id); 
  
  virtual grpc::Status GetSampledInfo(grpc::ServerContext* context, const ::google::protobuf::Empty* request, ::SampledInfo* response);
  virtual grpc::Status GetSampleBufferInfo(grpc::ServerContext* context, const ::SampleBufferInfoQuery* request, ::SampleBufferInfo* response);
  virtual grpc::Status SetSamples(grpc::ServerContext* context, const ::SampleData* request, ::SetSamplesResponse* response);
  virtual grpc::Status GetSamples(grpc::ServerContext* context, const ::GetSamplesRequest* request, ::SampleData* response);

  virtual grpc::Status SetOneShot(grpc::ServerContext* context, const ::OneShot * request, ::google::protobuf::Empty* response);

  virtual grpc::Status GetChannelEnable(grpc::ServerContext* context, const ::BufferId* request, ::ChannelEnable* response);
  virtual grpc::Status SetChannelEnable(grpc::ServerContext* context, const ::ChannelEnable* request, ::google::protobuf::Empty* response);

  
  virtual grpc::Status Trigger(grpc::ServerContext* context, const ::google::protobuf::Empty* request, ::google::protobuf::Empty* response);
};

sampled::sampled()
{
  int i;
  
  for (i = 0; i < 8; i++) {
    adc_buffers[i] = new piradio::sample_buffer(piradio::sample_buffer::IN, i);

    adc_buffers[i]->set_i_en(true);
    adc_buffers[i]->set_q_en(true);
  }

  for (i = 0; i < 8; i++) {
    dac_buffers[i] = new piradio::sample_buffer(piradio::sample_buffer::OUT, i);
  }
}

std::tuple<grpc::Status, piradio::sample_buffer *> sampled::get_buffer(const BufferId &id)
{
  piradio::sample_buffer *buffer;

  if (id.direction() == ADC) {
    if (id.buffer_no() >= n_adc_buffers()) {
      return std::make_tuple(grpc::Status(grpc::StatusCode::INVALID_ARGUMENT, "Buffer number invalid"), nullptr);
    }

    buffer = adc_buffers[id.buffer_no()];
  } else if(id.direction() == DAC) {
    if (id.buffer_no() >= n_dac_buffers()) {
      return std::make_tuple(grpc::Status(grpc::StatusCode::INVALID_ARGUMENT, "Buffer number invalid"), nullptr);
    }

    buffer = dac_buffers[id.buffer_no()];
  } else {
    return std::make_tuple(grpc::Status(grpc::StatusCode::INVALID_ARGUMENT, "Direction invalid"), nullptr);
  }
  
  return std::make_tuple(grpc::Status::OK, buffer);
}


grpc::Status sampled::GetSampledInfo(grpc::ServerContext* context, const ::google::protobuf::Empty* request, ::SampledInfo* response)
{
  response->set_n_adc_buffers(n_adc_buffers());
  response->set_n_dac_buffers(n_dac_buffers());

  return grpc::Status::OK;
}

grpc::Status sampled::GetSampleBufferInfo(grpc::ServerContext* context, const SampleBufferInfoQuery* request, ::SampleBufferInfo* response)
{
  grpc::Status retval;
  piradio::sample_buffer *buffer;

  std::tie(retval, buffer) = get_buffer(request->buffer_id());

  if (buffer == nullptr) {
    return retval;
  }
    
  response->set_nsamples(buffer->get_view<piradio::complex_sample>().nsamples());
  response->set_sample_rate(2e9);
  
  return grpc::Status::OK;
}

grpc::Status sampled::SetSamples(grpc::ServerContext* context, const ::SampleData* request, ::SetSamplesResponse* response)
{
  grpc::Status retval;
  piradio::sample_buffer *buffer;

  std::tie(retval, buffer) = get_buffer(request->buffer_id());

  if (buffer == nullptr) {
    return retval;
  }

  auto dst = buffer->raw_data<int16_t>();

  const auto &samples = request->samples();
  
  if (samples.size() > buffer->nbytes()) {
    return grpc::Status(grpc::StatusCode::INVALID_ARGUMENT, "Buffer too large");
  }
  
  memcpy(dst, samples.data(), samples.size());

  response->set_result(0);
  
  return grpc::Status::OK;
}

std::mutex output_mutex;

grpc::Status sampled::GetSamples(grpc::ServerContext* context, const ::GetSamplesRequest* request, ::SampleData* response)
{
  grpc::Status retval;
  piradio::sample_buffer *buffer;

  const auto &bid = request->buffer_id();
  
  std::tie(retval, buffer) = get_buffer(bid);

  if (buffer == nullptr) {
    return retval;
  }

  auto view = buffer->get_view<piradio::complex_sample>();
  
  *response->mutable_buffer_id() = request->buffer_id();
  response->set_nsamples(view.nsamples());
  response->set_samples(buffer->raw_data<uint8_t>(), buffer->nbytes());
  
  return grpc::Status::OK;
}

grpc::Status sampled::SetOneShot(grpc::ServerContext* context, const ::OneShot * request, ::google::protobuf::Empty* response)
{
  grpc::Status retval;
  piradio::sample_buffer *buffer;

  std::tie(retval, buffer) = get_buffer(request->buffer_id());
  
  if (buffer == nullptr) {
    return retval;
  }

  buffer->set_one_shot(request->one_shot());

  return grpc::Status::OK;
}

grpc::Status sampled::Trigger(grpc::ServerContext* context, const ::google::protobuf::Empty* request, ::google::protobuf::Empty* response)
{
  trigger.activate();

  return grpc::Status::OK;
}

grpc::Status sampled::GetChannelEnable(grpc::ServerContext* context, const ::BufferId* request, ::ChannelEnable* response)
{
  grpc::Status retval;
  piradio::sample_buffer *buffer;

  std::tie(retval, buffer) = get_buffer(*request);
  
  if (buffer == nullptr) {
    return retval;
  }

  *response->mutable_buffer_id() = *request;
  response->set_i(buffer->get_i_en());
  response->set_q(buffer->get_q_en());

  return grpc::Status::OK;
}

grpc::Status sampled::SetChannelEnable(grpc::ServerContext* context, const ::ChannelEnable* request, ::google::protobuf::Empty* response)
{
  grpc::Status retval;
  piradio::sample_buffer *buffer;

  std::tie(retval, buffer) = get_buffer(request->buffer_id());

  if (buffer == nullptr) {
    return retval;
  }

  buffer->set_i_en(request->i());
  buffer->set_q_en(request->q());

  return grpc::Status::OK;  
}

class sampled_daemon : public piradio::daemon
{
public:
  sampled_daemon() : daemon("io.pi-rad.sampled")
  {
    
  }

  virtual int prepare(void) {
    std::string server_address("0.0.0.0:7778");

    grpc::reflection::InitProtoReflectionServerBuilderPlugin();
 
    grpc::ServerBuilder builder;

    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    builder.RegisterService(&grpc_service);
    
    grpc_server = builder.BuildAndStart();

    return 0;
  }

  virtual int service_loop(void) {
    while(true) {
      std::shared_ptr<piradio::daemon_event> event = wait_event();

      if (event->is_a<piradio::daemon_reload_event>()) {
	continue;
      } else if (event->is_a<piradio::daemon_shutdown_event>()) {
	break;
      }
    }

    return 0;
  }
  
  
private:
  sampled grpc_service;
  
  std::unique_ptr<grpc::Server> grpc_server;
};


void run_server(void)
{
  
  //server->Wait();
}

int main(int argc, char **argv)
{
  sampled_daemon d;

  d.start();

  return d.wait_on();
}
