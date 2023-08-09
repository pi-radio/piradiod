include(../cmake/piradio.cmake)

piradio_project("piradio-zcu111d" ZCU111D)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --std=c++20 -g")

include(${MACRO_DIR}/changelog.cmake)
include(${MACRO_DIR}/copyright.cmake)
include(${MACRO_DIR}/grpc.cmake)

grpc_generate_interface("../interfaces/zcu111.proto")

include_directories("${CMAKE_CURRENT_SOURCE_DIR}/../libpiradio/include")    
include_directories("${CMAKE_CURRENT_SOURCE_DIR}/../libtilmx/include")    

include_directories("include")


add_executable(zcu111d
  src/i2c.cxx
  src/clocks.cxx
  src/LMX_regs.cxx
  src/zcu111d.cxx
  )


target_link_libraries(zcu111d
  tilmx
  piradio
  fmt
  i2c
  )

target_compile_options(zcu111d PUBLIC -g)

install(TARGETS zcu111d DESTINATION usr/bin COMPONENT ZCU111D)
piradio_install_dbus("io.piradio.zcu111d")
