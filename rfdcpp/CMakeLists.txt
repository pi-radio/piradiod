cmake_minimum_required (VERSION 3.0)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++20 -g")

include_directories (./include)

project(xrfdcpp)

set(LIBXRFDCPP_SOURCES src/xrfdcpp.cpp src/tile.cpp src/adc.cpp src/dac.cpp src/mixer.cpp)


add_library(xrfdcpp SHARED ${LIBXRFDCPP_SOURCES})
add_library(xrfdcpp_static STATIC ${LIBXRFDCPP_SOURCES})

find_package(pybind11 CONFIG)

pybind11_add_module(xrfdcpy src/pymod.cpp)
target_link_libraries(xrfdcpy PRIVATE xrfdcpp)

include_directories(Python3_INCLUDE_DIRS)



add_executable(rfdcstatus src/rfdcstatus.cpp)
target_link_libraries(rfdcstatus xrfdcpp)
