# Copyright 2018 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# cmake build file for C++ route_guide example.
# Assumes protobuf and gRPC have been installed using cmake.
# See cmake_externalproject/CMakeLists.txt for all-in-one cmake build
# that automatically builds all the dependencies before building route_guide.

cmake_minimum_required(VERSION 3.8)

project(piradiosampled C CXX)

#include(../cmake/common.cmake)

# Proto file
get_filename_component(sampled_proto "sampled.proto" ABSOLUTE)
get_filename_component(sampled_proto_path "${sampled_proto}" PATH)

set(_PROTOBUF_PROTOC protoc)
set(_GRPC_CPP_PLUGIN_EXECUTABLE /usr/bin/grpc_cpp_plugin)

# Generated sources
set(sampled_proto_srcs "${CMAKE_CURRENT_BINARY_DIR}/sampled.pb.cc")
set(sampled_proto_hdrs "${CMAKE_CURRENT_BINARY_DIR}/sampled.pb.h")
set(sampled_grpc_srcs "${CMAKE_CURRENT_BINARY_DIR}/sampled.grpc.pb.cc")
set(sampled_grpc_hdrs "${CMAKE_CURRENT_BINARY_DIR}/sampled.grpc.pb.h")
add_custom_command(
      OUTPUT "${sampled_proto_srcs}" "${sampled_proto_hdrs}" "${sampled_grpc_srcs}" "${sampled_grpc_hdrs}"
      COMMAND ${_PROTOBUF_PROTOC}
      ARGS --grpc_out "${CMAKE_CURRENT_BINARY_DIR}"
        --cpp_out "${CMAKE_CURRENT_BINARY_DIR}"
        -I "${sampled_proto_path}"
        --plugin=protoc-gen-grpc="${_GRPC_CPP_PLUGIN_EXECUTABLE}"
        "${sampled_proto}"
      DEPENDS "${sampled_proto}")

# Include generated *.pb.h files
include_directories("${CMAKE_CURRENT_BINARY_DIR}")

include_directories("${CMAKE_CURRENT_SOURCE_DIR}/../libsamplebuf/include")
link_directories("${CMAKE_CURRENT_SOURCE_DIR}/../libsamplebuf/build")

# sampled_grpc_proto
add_library(sampled_grpc_proto
  ${sampled_grpc_srcs}
  ${sampled_grpc_hdrs}
  ${sampled_proto_srcs}
  ${sampled_proto_hdrs})

target_link_options(sampled_grpc_proto PRIVATE "LINKER:-no-as-needed")

target_link_libraries(sampled_grpc_proto
  grpc++_reflection
  grpc++
  protobuf
  samplebuf
  fmt
  )

add_executable(piradio-sampled piradio-sampled.cxx)
target_link_libraries(piradio-sampled 
    sampled_grpc_proto)
#    ${_REFLECTION}
#    ${_GRPC_GRPCPP}
#    ${_PROTOBUF_LIBPROTOBUF})
