cmake_minimum_required (VERSION 3.0)

find_package(Python3 COMPONENTS Interpreter Development Development.Module)

#set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++20 -g")

#include_directories (./include ${Python3_INCLUDE_DIRS})

project(zcu111-set-clocks)

set(ZCU111_SET_CLOCKS_SOURCES zcu111-set-clocks.cpp)

add_executable(zcu111-set-clocks ${ZCU111_SET_CLOCKS_SOURCES})
#target_link_libraries(gensine pirsamp ${Python3_LIBRARIES})
