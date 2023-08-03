cmake_minimum_required (VERSION 3.0)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --std=c++20 -g")

include_directories(./include)

project(libsamplebuf VERSION 0.1.0 DESCRIPTION "Utilities for Pi Radio sample buffers")

set(LIBSAMPLEBUF_SOURCES src/samplebuf.cpp src/trigger.cpp src/uio.cpp)

add_library(samplebuf STATIC ${LIBSAMPLEBUF_SOURCES})

target_link_libraries(samplebuf PUBLIC fmt)

add_executable(piradio-dumpbuf src/dumpbuf.cpp)

target_link_libraries(piradio-dumpbuf samplebuf fmt)

add_executable(piradio-fillbuf src/fillbuf.cpp)

target_link_libraries(piradio-fillbuf samplebuf fmt boost_program_options)
