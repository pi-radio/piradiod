#!/bin/bash
set -e

if [ ! -f build/Makefile ] ; then
    mkdir -p build
    cd build
    cmake ..
else
    cd build
fi

make
cpack
sudo dpkg --force-all -i *.deb
