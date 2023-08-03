macro(grpc_generate_interface interface)
  get_filename_component(_proto "${interface}" ABSOLUTE)
  get_filename_component(_proto_path "${_proto}" DIRECTORY)
  get_filename_component(_proto_name "${_proto}" NAME_WLE)

  set(_PROTOBUF_PROTOC protoc)
  set(_GRPC_CPP_PLUGIN_EXECUTABLE /usr/bin/grpc_cpp_plugin)

  # Generated sources
  set(${_proto_name}_proto_srcs "${CMAKE_CURRENT_BINARY_DIR}/${_proto_name}.pb.cc")
  set(${_proto_name}_proto_hdrs "${CMAKE_CURRENT_BINARY_DIR}/${_proto_name}.pb.h")
  set(${_proto_name}_grpc_srcs "${CMAKE_CURRENT_BINARY_DIR}/${_proto_name}.grpc.pb.cc")
  set(${_proto_name}_grpc_hdrs "${CMAKE_CURRENT_BINARY_DIR}/${_proto_name}.grpc.pb.h")

  add_custom_command(
    OUTPUT "${${_proto_name}_proto_srcs}" "${${_proto_name}_proto_hdrs}" "${${_proto_name}_grpc_srcs}" "${${_proto_name}_grpc_hdrs}"
    COMMAND ${_PROTOBUF_PROTOC}
    ARGS --grpc_out "${CMAKE_CURRENT_BINARY_DIR}"
    --cpp_out "${CMAKE_CURRENT_BINARY_DIR}"
    -I "${_proto_path}"
    --plugin=protoc-gen-grpc="${_GRPC_CPP_PLUGIN_EXECUTABLE}"
    "${_proto}"
    DEPENDS "${_proto}"
    )

  #link_libraries("grpc++_reflection" "grpc" "protobuf")
  add_library(${_proto_name}_grpc_proto STATIC
    ${${_proto_name}_grpc_srcs}
    ${${_proto_name}_grpc_hdrs}
    ${${_proto_name}_proto_srcs}
    ${${_proto_name}_proto_hdrs})
  
  target_link_options(${_proto_name}_grpc_proto PRIVATE "LINKER:-no-as-needed")

  include_directories("${CMAKE_CURRENT_BINARY_DIR}")
  link_directories("${CMAKE_CURRENT_BINARY_DIR}")
  link_libraries("${_proto_name}_grpc_proto")
      
endmacro()
