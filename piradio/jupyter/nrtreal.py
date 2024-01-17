import sys
import time
import numpy as np

from piradio.util import GHz
from piradio.devices import SampleBufferIn, SampleBufferOut, Trigger, REAL_SAMPLES

from .nrt_common import *

sbis = [ SampleBufferIn(i, sample_rate=GHz(4), sample_format=REAL_SAMPLES) for i in range(8) ]
sbos = [ SampleBufferOut(i, sample_rate=GHz(4), sample_format=REAL_SAMPLES) for i in range(8) ]

nrt_setup(sys.modules[__name__])


