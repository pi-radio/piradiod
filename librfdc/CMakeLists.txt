include(../cmake/piradio.cmake)

piradio_project("librfdc" LIBRFDC)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DKS_STR_ENCODING_NONE --std=c++20 -g")

include_directories("include")

include_directories("${CMAKE_CURRENT_SOURCE_DIR}/../libpiradio/include")    

add_library(xrfdc STATIC
  src/xilinx/xrfdc.c
  src/xilinx/xrfdc_ap.c
  src/xilinx/xrfdc_dp.c
  src/xilinx/xrfdc_clock.c
  src/xilinx/xrfdc_g.c
  src/xilinx/xrfdc_intr.c
  src/xilinx/xrfdc_mb.c
  src/xilinx/xrfdc_mixer.c
  src/xilinx/xrfdc_mts.c
  src/xilinx/xrfdc_sinit.c
)

add_library(rfdc SHARED
  src/rfdc.cxx
  src/rfdc_tile.cxx
  src/rfdc_dc.cxx
  src/rfdc_adc.cxx
  src/rfdc_dac.cxx
  src/rfdc_str.cxx
  )

target_compile_options(xrfdc PUBLIC -g)

target_link_libraries(rfdc
  xrfdc)

target_compile_options(rfdc PUBLIC -g)


add_executable(rfdcnco
  src/rfdcnco.cxx)

target_link_libraries(rfdcnco rfdc metal)
target_compile_options(rfdcnco PUBLIC -g)

add_executable(rfdc_disable_nco
  src/rfdc_disable_nco.cxx)

target_link_libraries(rfdc_disable_nco rfdc metal)
target_compile_options(rfdc_disable_nco PUBLIC -g)

add_executable(rfdcmix
  src/rfdcmix.cxx)

target_link_libraries(rfdcmix rfdc metal)
target_compile_options(rfdcmix PUBLIC -g)
