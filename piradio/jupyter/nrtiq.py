import time
import numpy as np

from piradio.devices import SampleBufferIn, SampleBufferOut, Trigger
from .nrt_common import *

sbos = [ SampleBufferOut(i) for i in range(8) ]
sbis = [ SampleBufferIn(i) for i in range(8) ]

nrt_setup(sys.modules[__name__])


