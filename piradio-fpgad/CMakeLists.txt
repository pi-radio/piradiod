cmake_minimum_required(VERSION 3.8)

include(GNUInstallDirs)

project(piradio-fpgad C CXX)

find_package(sdbus-c++ REQUIRED)

include_directories("include")


add_executable(piradio-fpgad src/fpga.cxx src/fpgad.cxx)
target_link_libraries(piradio-fpgad
  SDBusCpp::sdbus-c++
  systemd)

target_compile_options(piradio-fpgad PUBLIC -g)
target_compile_options(piradio-fpgad PUBLIC -g)

install(FILES conf/io.pi-rad.fpgad.conf DESTINATION etc/dbus-1/system.d/)
install(FILES conf/piradio-fpgad.service DESTINATION etc/systemd/system)

set(CPACK_SET_DESTDIR true)
set(CPACK_INSTALL_PREFIX /)
set(CPACK_GENERATOR DEB)
set(CPACK_PACKAGE_NAME "piradio-fpgad")
set(CPACK_PACKAGE_VENDOR "Pi Radio Inc.")
set(CPACK_PACKAGE_CONTACT "Michael Zappe <zapman@pi-rad.io>")
include(CPack)
