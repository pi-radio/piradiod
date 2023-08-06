include(../cmake/piradio.cmake)

piradio_project("piradio-rfdcd" RFDCD)

include(${MACRO_DIR}/changelog.cmake)
include(${MACRO_DIR}/copyright.cmake)

find_package(sdbus-c++ REQUIRED)


# Proto file
get_filename_component(rfdcd_proto "../interfaces/rfdcd.proto" ABSOLUTE)
get_filename_component(rfdcd_proto_path "${rfdcd_proto}" PATH)

set(_PROTOBUF_PROTOC protoc)
set(_GRPC_CPP_PLUGIN_EXECUTABLE /usr/bin/grpc_cpp_plugin)

# Generated sources
set(rfdcd_proto_srcs "${CMAKE_CURRENT_BINARY_DIR}/rfdcd.pb.cc")
set(rfdcd_proto_hdrs "${CMAKE_CURRENT_BINARY_DIR}/rfdcd.pb.h")
set(rfdcd_grpc_srcs "${CMAKE_CURRENT_BINARY_DIR}/rfdcd.grpc.pb.cc")
set(rfdcd_grpc_hdrs "${CMAKE_CURRENT_BINARY_DIR}/rfdcd.grpc.pb.h")
add_custom_command(
      OUTPUT "${rfdcd_proto_srcs}" "${rfdcd_proto_hdrs}" "${rfdcd_grpc_srcs}" "${rfdcd_grpc_hdrs}"
      COMMAND ${_PROTOBUF_PROTOC}
      ARGS --grpc_out "${CMAKE_CURRENT_BINARY_DIR}"
        --cpp_out "${CMAKE_CURRENT_BINARY_DIR}"
        -I "${rfdcd_proto_path}"
        --plugin=protoc-gen-grpc="${_GRPC_CPP_PLUGIN_EXECUTABLE}"
        "${rfdcd_proto}"
      DEPENDS "${rfdcd_proto}")


include_directories("${CMAKE_CURRENT_SOURCE_DIR}/../libpiradio/include")    

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


add_executable(piradio-rfdcd
  src/rfdcd.cxx
  src/rfdc.cxx
  src/rfdc_tile.cxx
  src/rfdc_dc.cxx
  src/rfdc_adc.cxx
  src/rfdc_dac.cxx
  src/rfdc_str.cxx
  )


target_link_libraries(piradio-rfdcd
  SDBusCpp::sdbus-c++
  piradio
  rfdc
  metal
  fmt
  i2c
  )

target_compile_options(piradio-rfdcd PUBLIC -g)
target_compile_options(rfdc PUBLIC -g)

install(TARGETS piradio-rfdcd DESTINATION usr/bin COMPONENT RFDCD)
piradio_install_dbus("io.piradio.rfdcd")

