cmake_minimum_required(VERSION 3.8)

project(zcu111d
  VERSION 0.1.0
  DESCRIPTION "ZCU111 control daemon"
  HOMEPAGE_URL "https://pi-rad.io/"
  LANGUAGES CXX)

include(GNUInstallDirs)


find_package(sdbus-c++ REQUIRED)


# Proto file
get_filename_component(zcu111d_proto "../interfaces/zcu111d.proto" ABSOLUTE)
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

add_library(rfdc STATIC
  src/xilinx/xrfdc.c
  src/xilinx/xrfdc_ap.c
  src/xilinx/xrfdc_dp.c
  src/xilinx/xrfdc_clock.c
  src/xilinx/xrfdc_g.c
  src/xilinx/xrfdc_intr.c
  src/xilinx/xrfdc_mb.c
  src/xilinx/xrfdc_mixer.c
  src/xilinx/xrfdc_mts.c
  src/xilinx/xrfdc_sinit.c
)


add_executable(zcu111d
  src/i2c.cxx
  src/clocks.cxx
  src/zcu111d.cxx
  src/rfdc.cxx
  src/rfdc_tile.cxx
  src/rfdc_dc.cxx
  src/rfdc_adc.cxx
  src/rfdc_dac.cxx
  src/rfdc_str.cxx
  )


target_link_libraries(zcu111d
  SDBusCpp::sdbus-c++
  pidaemon
  rfdc
  metal
  fmt
  i2c
  )

target_compile_options(zcu111d PUBLIC -g)
target_compile_options(rfdc PUBLIC -g)

install(FILES conf/io.pi-rad.zcu111d.conf DESTINATION etc/dbus-1/system.d/)
install(FILES conf/zcu111d.service DESTINATION etc/systemd/system)

set(CPACK_SET_DESTDIR true)
set(CPACK_INSTALL_PREFIX /)
set(CPACK_GENERATOR DEB)
set(CPACK_PACKAGE_NAME "piradio-zcu111d")
set(CPACK_PACKAGE_VENDOR "Pi Radio Inc.")
set(CPACK_PACKAGE_CONTACT "Michael Zappe <zapman@pi-rad.io>")
set(CPACK_OUTPUT_CONFIG_FILE "${CMAKE_BINARY_DIR}/zcu111_cpack.cmake")

include(CPack)

