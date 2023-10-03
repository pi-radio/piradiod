include(../cmake/piradio.cmake)

piradio_project("piradio-siversd" SIVERSD)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DKS_STR_ENCODING_NONE --std=c++20 -g")

include(${MACRO_DIR}/changelog.cmake)
include(${MACRO_DIR}/copyright.cmake)
include(${MACRO_DIR}/grpc.cmake)

add_custom_target(siversd
  DEPENDS "siversd_pb2.py" "siversd_pb2_grpc.py"
)

python_add_protocol(siversd)
