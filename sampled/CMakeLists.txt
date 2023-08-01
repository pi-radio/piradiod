include(../cmake/piradio.cmake)

piradio_project("piradio-sampled" SAMPLED)

include(${MACRO_DIR}/changelog.cmake)
include(${MACRO_DIR}/copyright.cmake)

# Proto file
get_filename_component(sampled_proto "../interfaces/sampled.proto" ABSOLUTE)
get_filename_component(sampled_proto_path "${sampled_proto}" PATH)

set(_PROTOBUF_PROTOC protoc)
set(_GRPC_CPP_PLUGIN_EXECUTABLE /usr/bin/grpc_cpp_plugin)

# Generated sources
set(sampled_proto_srcs "${CMAKE_CURRENT_BINARY_DIR}/sampled.pb.cc")
set(sampled_proto_hdrs "${CMAKE_CURRENT_BINARY_DIR}/sampled.pb.h")
set(sampled_grpc_srcs "${CMAKE_CURRENT_BINARY_DIR}/sampled.grpc.pb.cc")
set(sampled_grpc_hdrs "${CMAKE_CURRENT_BINARY_DIR}/sampled.grpc.pb.h")
add_custom_command(
      OUTPUT "${sampled_proto_srcs}" "${sampled_proto_hdrs}" "${sampled_grpc_srcs}" "${sampled_grpc_hdrs}"
      COMMAND ${_PROTOBUF_PROTOC}
      ARGS --grpc_out "${CMAKE_CURRENT_BINARY_DIR}"
        --cpp_out "${CMAKE_CURRENT_BINARY_DIR}"
        -I "${sampled_proto_path}"
        --plugin=protoc-gen-grpc="${_GRPC_CPP_PLUGIN_EXECUTABLE}"
        "${sampled_proto}"
      DEPENDS "${sampled_proto}")

# Include generated *.pb.h files
include_directories("${CMAKE_CURRENT_BINARY_DIR}")

include_directories("${CMAKE_CURRENT_SOURCE_DIR}/../libsamplebuf/include")
include_directories("${CMAKE_CURRENT_SOURCE_DIR}/../libpidaemon/include")
#link_directories("${CMAKE_CURRENT_SOURCE_DIR}/../libsamplebuf/build")
#link_directories("${CMAKE_CURRENT_SOURCE_DIR}/../libsamplebuf/build")

# sampled_grpc_proto
add_library(sampled_grpc_proto
  ${sampled_grpc_srcs}
  ${sampled_grpc_hdrs}
  ${sampled_proto_srcs}
  ${sampled_proto_hdrs})

target_link_options(sampled_grpc_proto PRIVATE "LINKER:-no-as-needed")

target_link_libraries(sampled_grpc_proto
  grpc++_reflection
  grpc++
  protobuf
  samplebuf
  fmt
  )

add_executable(piradio-sampled
  src/piradio-sampled.cxx)

target_link_libraries(piradio-sampled 
  sampled_grpc_proto
  pidaemon
  )
#    ${_REFLECTION}
#    ${_GRPC_GRPCPP}
#    ${_PROTOBUF_LIBPROTOBUF})

install(FILES conf/io.piradio.sampled.conf DESTINATION etc/dbus-1/system.d/ COMPONENT sampled)
install(FILES conf/io.piradio.sampled.service DESTINATION etc/systemd/system COMPONENT sampled)

install(TARGETS piradio-sampled DESTINATION usr/bin COMPONENT SAMPLED)
piradio_install_dbus("io.piradio.sampled")
