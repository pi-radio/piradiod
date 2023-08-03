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
sudo dpkg -r piradio-firmware-ucsb piradio-sampled piradio-zcu111d piradio-fpgad piradio-rfdcd piradio-base
sudo dpkg --force-all -i *.deb ~/piradio-firmware-*.deb
