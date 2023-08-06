include(../cmake/piradio.cmake)

piradio_project("piradio-sampled" SAMPLED)

include(${MACRO_DIR}/changelog.cmake)
include(${MACRO_DIR}/copyright.cmake)
include(${MACRO_DIR}/grpc.cmake)

grpc_generate_interface("../interfaces/sampled.proto")

include_directories("${CMAKE_CURRENT_SOURCE_DIR}/../libsamplebuf/include")
include_directories("${CMAKE_CURRENT_SOURCE_DIR}/../libpiradio/include")

link_libraries(piradio samplebuf fmt)

add_executable(piradio-sampled
  src/piradio-sampled.cxx)


install(FILES conf/io.piradio.sampled.conf DESTINATION etc/dbus-1/system.d/ COMPONENT sampled)
install(FILES conf/io.piradio.sampled.service DESTINATION etc/systemd/system COMPONENT sampled)

install(TARGETS piradio-sampled DESTINATION usr/bin COMPONENT SAMPLED)
piradio_install_dbus("io.piradio.sampled")
