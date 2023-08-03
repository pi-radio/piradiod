cmake_minimum_required (VERSION 3.0)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --std=c++20 -g")

include_directories(./include)

find_package(sdbus-c++ REQUIRED)

project(libpidaemon VERSION 0.1.0 DESCRIPTION "Shared class for Pi Radio Daemons")

set(LIBPIDAEMON_SOURCES src/daemon.cxx src/grpc.cxx)

add_library(pidaemon STATIC ${LIBPIDAEMON_SOURCES})

target_link_libraries(pidaemon PUBLIC
  grpc++_reflection
  grpc++
  grpc
  protobuf
  SDBusCpp::sdbus-c++
  systemd)

