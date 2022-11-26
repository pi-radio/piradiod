cmake_minimum_required (VERSION 3.0)

find_package(Python3 COMPONENTS Interpreter Development Development.Module)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++20 -g")

include_directories (./include ${Python3_INCLUDE_DIRS})

project(pirsamp)

set(LIBPIRSAMP_SOURCES src/pirsamp.cpp)

add_library(pirsamp SHARED ${LIBPIRSAMP_SOURCES})
add_library(pirsamp_static STATIC ${LIBPIRSAMP_SOURCES})

add_executable(gensine src/gensine.cpp)
target_link_libraries(gensine pirsamp ${Python3_LIBRARIES})

add_executable(readbuf src/readbuf.cpp)
target_link_libraries(readbuf pirsamp ${Python3_LIBRARIES})
