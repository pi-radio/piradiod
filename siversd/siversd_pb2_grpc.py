# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
import siversd_pb2 as siversd__pb2


class siversdStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.GetNumRadios = channel.unary_unary(
        '/siversd/GetNumRadios',
        request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        response_deserializer=siversd__pb2.NumRadios.FromString,
        )


class siversdServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def GetNumRadios(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_siversdServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'GetNumRadios': grpc.unary_unary_rpc_method_handler(
          servicer.GetNumRadios,
          request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
          response_serializer=siversd__pb2.NumRadios.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'siversd', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))