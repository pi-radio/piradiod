
cmake_minimum_required(VERSION 3.8)

project(piradio)


foreach(name IN ITEMS libsamplebuf libpidaemon piradio-sampled piradio-fpgad zcu111d)
  add_subdirectory("${name}")
  list(APPEND CPACK_INSTALL_CMAKE_PROJECTS "${CMAKE_CURRENT_BINARY_DIR};${name};ALL;${CMAKE_CURRENT_LIST_DIR}")
endforeach()  

include(CPack)
