include(../cmake/piradio.cmake)

piradio_project("piradio-fpgad" FPGAD)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DKS_STR_ENCODING_NONE --std=c++20 -g")

include(${MACRO_DIR}/changelog.cmake)
include(${MACRO_DIR}/copyright.cmake)
include(${MACRO_DIR}/grpc.cmake)

find_package(sdbus-c++ REQUIRED)

# Proto file
grpc_generate_interface("../interfaces/fpgad.proto")

include_directories("${CMAKE_CURRENT_SOURCE_DIR}/../libpiradio/include")    


include_directories("include")


add_executable(piradio-fpgad src/fpga.cxx src/fpgad.cxx)


target_link_libraries(piradio-fpgad
  piradio
  fmt
  SDBusCpp::sdbus-c++
  systemd)

target_compile_options(piradio-fpgad PUBLIC -g)

install(TARGETS piradio-fpgad DESTINATION usr/bin COMPONENT FPGAD)
piradio_install_dbus("io.piradio.fpgad")


