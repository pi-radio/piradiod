cmake_minimum_required (VERSION 3.0)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++20 -g")

include_directories (./include)

project(xrfdcpp)

set(LIBXRFDCPP_SOURCES src/xrfdcpp.cpp)

add_library(xrfdcpp SHARED ${LIBXRFDCPP_SOURCES})
add_library(xrfdcpp_static STATIC ${LIBXRFDCPP_SOURCES})

add_executable(rfdcstatus src/rfdcstatus.cpp)
target_link_libraries(rfdcstatus xrfdcpp)
