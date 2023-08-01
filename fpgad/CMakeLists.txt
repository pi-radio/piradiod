include(../cmake/piradio.cmake)

piradio_project("piradio-fpgad" FPGAD)

include(${MACRO_DIR}/changelog.cmake)
include(${MACRO_DIR}/copyright.cmake)

find_package(sdbus-c++ REQUIRED)

# Proto file
get_filename_component(fpgad_proto "../interfaces/fpgad.proto" ABSOLUTE)
get_filename_component(zcu111d_proto_path "${zcu111d_proto}" PATH)

set(_PROTOBUF_PROTOC protoc)
set(_GRPC_CPP_PLUGIN_EXECUTABLE /usr/bin/grpc_cpp_plugin)

# Generated sources
set(zcu111d_proto_srcs "${CMAKE_CURRENT_BINARY_DIR}/zcu111d.pb.cc")
set(zcu111d_proto_hdrs "${CMAKE_CURRENT_BINARY_DIR}/zcu111d.pb.h")
set(zcu111d_grpc_srcs "${CMAKE_CURRENT_BINARY_DIR}/zcu111d.grpc.pb.cc")
set(zcu111d_grpc_hdrs "${CMAKE_CURRENT_BINARY_DIR}/zcu111d.grpc.pb.h")
add_custom_command(
      OUTPUT "${zcu111d_proto_srcs}" "${zcu111d_proto_hdrs}" "${zcu111d_grpc_srcs}" "${zcu111d_grpc_hdrs}"
      COMMAND ${_PROTOBUF_PROTOC}
      ARGS --grpc_out "${CMAKE_CURRENT_BINARY_DIR}"
        --cpp_out "${CMAKE_CURRENT_BINARY_DIR}"
        -I "${zcu111d_proto_path}"
        --plugin=protoc-gen-grpc="${_GRPC_CPP_PLUGIN_EXECUTABLE}"
        "${zcu111d_proto}"
      DEPENDS "${zcu111d_proto}")


include_directories("${CMAKE_CURRENT_SOURCE_DIR}/../libpidaemon/include")    


include_directories("include")


add_executable(piradio-fpgad src/fpga.cxx src/fpgad.cxx)
target_link_libraries(piradio-fpgad
  pidaemon
  grpc++_reflection
  grpc++
  protobuf
  fmt
  SDBusCpp::sdbus-c++
  systemd)

target_compile_options(piradio-fpgad PUBLIC -g)

install(TARGETS piradio-fpgad DESTINATION usr/bin COMPONENT FPGAD)
piradio_install_dbus("io.piradio.fpgad")


