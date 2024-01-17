import time
import numpy as np

from piradio.devices import SampleBufferIn, SampleBufferOut, Trigger

from .nrt_common import set_sample_bufs

set_sample_bufs([ SampleBufferIn(i) for i in range(8) ], [ SampleBufferOut(i) for i in range(8) ])

from .nrt_common import *
