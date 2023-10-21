include(../cmake/piradio.cmake)

piradio_project("libzcu111" LIBZCU111)

add_library(zcu111 STATIC
  src/zcu111.cxx
  src/clocks.cxx
  src/i2c.cxx
  )

include_directories("include")
include_directories("${CMAKE_CURRENT_SOURCE_DIR}/../libpiradio/include")    
include_directories("${CMAKE_CURRENT_SOURCE_DIR}/../libtilmx/include")    
include_directories("${CMAKE_CURRENT_SOURCE_DIR}/../librfdc/include")    

target_compile_options(zcu111 PUBLIC -g --std=c++20)
target_link_libraries(zcu111
  tilmx
  piradio
  fmt
  )

add_executable(zcu111-util
  src/zcu111_util.cxx
  src/zcu111_predef_lmx.cxx
  )

target_link_libraries(zcu111-util
  zcu111
  tilmx
  piradio
  fmt
  i2c
  )
