#!/usr/bin/env python3
import os
import sys
import base64
import click

from io import BytesIO

import numpy as np
from numpy.lib import format as npf

from twisted.web import xmlrpc, server
from twisted.internet import reactor, endpoints

from piradio.util import MHz, GHz, Freq
from piradio.devices import SampleBufferIn, SampleBufferOut, Trigger
from piradio.devices import Trigger



class PiRadio_NRT_XMLRPC(xmlrpc.XMLRPC):
    def __init__(self):
        self.input_samples = [ SampleBufferIn(i) for i in range(8) ]
        self.output_samples = [ SampleBufferOut(i) for i in range(8) ]
        self.trigger = Trigger()

        for s in self.input_samples:
            s.one_shot(True)

        for s in self.output_samples:
            s.one_shot(False)
            
        super().__init__(allowNone=True)
        
    def xmlrpc_get_samples(self, direction, n):
        if n < 0 or n > 7:
            raise xmlrpc.Fault(123, "Invalid buffer number")

        f = BytesIO()
        
        if direction == 'input':
            npf.write_array(f, self.input_samples[n].array)
        elif direction == 'output':
            npf.write_array(f, self.output_samples[n].array)
        else:
            raise xmlrpc.Fault(123, "Invalid direction")

        return base64.b64encode(f.getvalue())

    def xmlrpc_set_samples(self, n, samples):
        if n < 0 or n > 7:
            raise xmlrpc.Fault(123, "Invalid buffer number")

        a = npf.read_array(BytesIO(base64.b64decode(samples)))

        self.output_samples[n].array = a

        return True
        

    def xmlrpc_fill_freq(self, n, f, phase = 0):
        if n < 0 or n > 7:
            raise xmlrpc.Fault(123, "Invalid buffer number")

        f = Freq(f)

        self.output_samples[n].fill_sine(f, phase)

        return True

    def xmlrpc_fill_chirp(self, n, f, phase = 0):
        if n < 0 or n > 7:
            raise xmlrpc.Fault(123, "Invalid buffer number")

        f = Freq(f)

        self.output_samples[n].fill_chirp(f, phase)

        return True
    
    def xmlrpc_fill_Zadoff_Chu(self, n, Nzc : int, u : int, q : int):
        if n < 0 or n > 7:
            raise xmlrpc.Fault(123, "Invalid buffer number")

        self.output_samples[n].fill_Zadoff_Chu(Nzc, u, q)

        return True

    def xmlrpc_global_trigger(self):
        self.trigger.trigger()

    def xmlrpc_one_shot(self, n, direction, b):
        if n < 0 or n > 7:
            raise xmlrpc.Fault(123, "Invalid buffer number")

        if direction == 'input':
            self.input_samples[n].one_shot(b)
        elif direction == 'output':
            self.output_samples[n].one_shot(b)
        else:
            raise xmlrpc.Fault(123, "Invalid direction")

        return True

        

    

@click.command()
def piradionrt():
    with open("/sys/class/fpga_manager/fpga0/state", "r") as f:
        if f.read().strip() != "operating":
            print("FPGA not programmed")
            sys.exit(1)

    rpc = PiRadio_NRT_XMLRPC()

    endpoint = endpoints.TCP4ServerEndpoint(reactor, 7777)
    endpoint.listen(server.Site(rpc))

    reactor.run()


if __name__ == '__main__':
    piradionrt()
