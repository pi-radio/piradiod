cmake_minimum_required(VERSION 3.8)

project(zcu111d C CXX)

find_package(sdbus-c++ REQUIRED)

include_directories("include")


add_executable(piradio-fpgad src/fpga.cxx src/fpgad.cxx)
target_link_libraries(piradio-fpgad
  SDBusCpp::sdbus-c++
  systemd)

target_compile_options(piradio-fpgad PUBLIC -g)
target_compile_options(piradio-fpgad PUBLIC -g)

install(FILES conf/io.pi-rad.fpgad.conf DESTINATION /etc/dbus-1/system.d/)
install(FILES conf/piradio-fpgad.service DESTINATION /etc/systemd/system)
