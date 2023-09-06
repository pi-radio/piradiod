include(../cmake/piradio.cmake)

piradio_project("piradio-fpgad" FPGAD)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DKS_STR_ENCODING_NONE --std=c++20 -g")

include(${MACRO_DIR}/changelog.cmake)
include(${MACRO_DIR}/copyright.cmake)
include(${MACRO_DIR}/grpc.cmake)

find_package(sdbus-c++ REQUIRED)

# Proto file
grpc_generate_interface("../interfaces/fpgad.proto")
grpc_generate_interface("../interfaces/zcu111.proto")
grpc_generate_interface("../interfaces/rfdcd.proto")

include_directories("${CMAKE_CURRENT_SOURCE_DIR}/../libpiradio/include")    
include_directories("${CMAKE_CURRENT_SOURCE_DIR}/../libtilmx/include")    


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

add_executable(piradio-fpgad
  src/fpga.cxx
  src/fpgad.cxx
  src/i2c.cxx
  src/clocks.cxx
  src/rfdc.cxx
  src/rfdc_tile.cxx
  src/rfdc_dc.cxx
  src/rfdc_adc.cxx
  src/rfdc_dac.cxx
  src/rfdc_str.cxx
  src/zcu111.cxx
  src/rfdc_manager.cxx
  #src/rfdcd.cxx
  #src/zcu111d.cxx
)


target_link_libraries(piradio-fpgad
  tilmx
  rfdc
  piradio
  fmt
  SDBusCpp::sdbus-c++
  systemd
  i2c
  metal
  )

target_compile_options(piradio-fpgad PUBLIC -g)

install(TARGETS piradio-fpgad DESTINATION usr/bin COMPONENT FPGAD)
piradio_install_dbus("io.piradio.fpgad")


