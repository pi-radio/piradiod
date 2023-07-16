#!/usr/bin/env python3
import os
import sys
import base64
import click
import daemonize

from io import BytesIO

import numpy as np
#from numpy.lib import format as npf

#from twisted.web import xmlrpc, server
#from twisted.internet import reactor, endpoints

from piradio.util import MHz, GHz, Freq
from piradio.devices import SampleBufferIn, SampleBufferOut, Trigger
from piradio.devices import Trigger

class _NRT:
    def __init__(self):
        self.input_samples = [ SampleBufferIn(i) for i in range(8) ]
        self.output_samples = [ SampleBufferOut(i) for i in range(8) ]
        self.trigger = Trigger()

_nrt = None
        
def NRT():
    global _nrt
    
    if _nrt is None:
        _nrt = _NRT()
        
    return _nrt
    
