import time
import numpy as np

from piradio.devices import SampleBufferIn, SampleBufferOut, Trigger
from .nrt_common import set_sample_bufs

sbos = [ SampleBufferOut(i) for i in range(8) ]
sbis = [ SampleBufferIn(i) for i in range(8) ]


