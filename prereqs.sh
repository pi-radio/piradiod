#!/bin/bash

git submodule update --init --recursive

sudo apt install -y libsdbus-c++-dev python3-click-man protobuf-compiler protobuf-compiler-grpc libgrpc-dev libgrpc++-dev grpc-proto python3-grpc-tools python3-grpcio libfmt-dev libi2c-dev
