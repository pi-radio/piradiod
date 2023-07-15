#!/bin/bash

sudo /bin/bash -c "cp udev/40-piradio.rules /etc/udev/rules.d && udevadm control --reload-rules && udevadm trigger"
