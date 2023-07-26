cmake_minimum_required(VERSION 3.8)

project(zcu111d C CXX)

find_package(sdbus-c++ REQUIRED)

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


add_executable(zcu111d src/zcu111d.cxx src/rfdc.cxx src/rfdc_tile.cxx src/rfdc_dc.cxx src/rfdc_str.cxx)
target_link_libraries(zcu111d
  SDBusCpp::sdbus-c++
  rfdc
  metal)

target_compile_options(zcu111d PUBLIC -g)
target_compile_options(rfdc PUBLIC -g)

install(FILES conf/io.pi-rad.zcu111d.conf DESTINATION /etc/dbus-1/system.d/)
install(FILES conf/zcu111d.service DESTINATION /etc/systemd/system)
