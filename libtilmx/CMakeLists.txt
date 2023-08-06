cmake_minimum_required (VERSION 3.0)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --std=c++20 -g")

include_directories(./include)

project(libtilmx VERSION 0.1.0 DESCRIPTION "TI LMXxxxx programming library")

set(LIBTILMX_SOURCES src/lmx2594.cxx src/lmx2594_config.cxx)

include_directories("${CMAKE_CURRENT_SOURCE_DIR}/../libpiradio/include")

add_library(tilmx STATIC ${LIBTILMX_SOURCES})

#target_link_libraries( PUBLIC)

