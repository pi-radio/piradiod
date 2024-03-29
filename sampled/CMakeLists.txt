include(../cmake/piradio.cmake)

piradio_project("piradio-sampled" SAMPLED)

include(GNUInstallDirs)

find_package(sdbus-c++ REQUIRED)

include(${MACRO_DIR}/changelog.cmake)
include(${MACRO_DIR}/copyright.cmake)
include(${MACRO_DIR}/grpc.cmake)

include_directories("${CMAKE_CURRENT_SOURCE_DIR}/../libsamplebuf/include")

link_libraries(
  samplebuf
  fmt
  piradio
  grpc++_reflection
  grpc++
  grpc
  protobuf
  SDBusCpp::sdbus-c++
  systemd  
)

add_executable(piradio-sampled
  src/sampled.cxx)

target_add_protocol(piradio-sampled sampled)

install(FILES conf/io.piradio.sampled.conf DESTINATION etc/dbus-1/system.d/ COMPONENT sampled)
install(FILES conf/io.piradio.sampled.service DESTINATION etc/systemd/system COMPONENT sampled)

install(TARGETS piradio-sampled DESTINATION usr/bin COMPONENT SAMPLED)
piradio_install_dbus("io.piradio.sampled")
