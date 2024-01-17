import time
import math
import copy
import struct
from pathlib import Path
from functools import cached_property
from threading import Timer
from scipy.signal import resample

import numpy as np
import numpy.fft as fft
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, decimate
import pandas as pd

from piradio.output import output
from piradio.command import command, cmdproperty
from piradio.devices.uio import UIO
from piradio.util import Freq, GHz, Samples, REAL_SAMPLES, IQ_SAMPLES

dt_uint32 = struct.Struct(">i")

uint32 = struct.Struct("I")
iq = struct.Struct("hh")

csr_struct = struct.Struct("iiiiii")

iq_struct = struct.Struct("hh")

def u2s(x):
    if x & (1 << 15):
        x = -((~x & 0xFFFF) + 1)
    return x
    


def int_to_iq(n, swap_IQ):
    I = u2s((n >> 16) & 0xFFFF)
    Q = u2s(n & 0xFFFF)

    return (I, Q) if not swap_IQ else (Q, I)

class IQBuf:
    def plot():
        pass

class SampleMap:
    def __init__(self, sbuf, sample_format):
        self.sbuf = sbuf
        self._format = sample_format
       
    def __getitem__(self, n):
        if self._format == IQ_SAMPLES:
            s = self.sbuf._samples[n * 4]
        
            if isinstance(s, list):
                return map(int_to_iq, s)
            else:
                return int_to_iq(s, self.sbuf.swap_IQ)
        elif self._format == REAL_SAMPLES:
            s = self.sbuf._samples[n * 2]
            
            if isinstance(s, list):
                return map(u2s, s)
            else:
                return u2s(s)
        else:
            raise RuntimeError("Not implemented")
 
    def __setitem__(self, n, v):
        if self._format == IQ_SAMPLES:
            if self.sbuf.swap_IQ:
                self.sbuf._samples[n * 4] = ((v[1] & 0xFFFF) << 16) | (v[0] & 0xFFFF) # uint32.unpack(iq.pack(*v))[0]
            else:
                self.sbuf._samples[n * 4] = ((v[0] & 0xFFFF) << 16) | (v[1] & 0xFFFF) # uint32.unpack(iq.pack(*v))[0]
        elif self._format == REAL_SAMPLES:
            self.sbuf._samples[n * 2] = v & 0xFFFF
        else:
            raise RuntimeError("Not implemented")

    def dump(self):
        if self._format == IQ_SAMPLES:
            for i in range(self.sbuf.start_sample, self.sbuf.end_sample):
                v = self[i]
                print(f"{i}: {v}")
        else:
            raise RuntimeError("Not implemented")
                
    @property
    def format(self):
        return self._format
            
    
class SampleBuffer(UIO):
    @property
    def is_sample_buffer(self):
        return True
    
    def __init__(self, n, direction, sample_rate=GHz(2), sample_format=IQ_SAMPLES):
        self.direction = direction
        self.n = n
        self.sample_rate=sample_rate
        self.sample_format = sample_format
        path = None

        for p in Path("/sys/bus/platform/devices").glob(f"*.axis_sample_buffer_{direction}"):
            with open(p / "of_node" / "sample-buffer-no", "rb") as f:
                v = dt_uint32.unpack(f.read())[0]
                if n == v:
                    output.debug(f"Found {p}")
                    path = p
                    break

        if path is None:
            raise RuntimeError(f"Could not find sample buffer {direction} {n}")
                
        super().__init__(path)

        self.csr = self.maps[0]
        self._samples = self.maps[1]

        self.csr.map()
        self._samples.map(cast='I' if sample_format == IQ_SAMPLES else 'H')
        
        self.sample_map = SampleMap(self, sample_format)
        
        assert self.ip_id == 0x5053424F, f"Invalid IP identifier {self.ip_id:x}"

        output.debug(f"CTRL STAT: {self.ctrl_stat}")
        output.debug(f"OFFSETS: {self.start_offset}-{self.end_offset}")
        output.debug(f"STREAM_DEPTH: {self.stream_depth}")
        output.debug(f"SIZE BYTES: {self.size_bytes}")

    def read_reg(self, n):
        return uint32.unpack(self.csr_map[4*n:4*n+4])[0]

    @property
    def i_en(self):
        return True if self.ctrl_stat & 0x20 else False

    @i_en.setter
    def i_en(self, v):
        if v:
            self.csr[4 * 1] = (self.csr[4 * 1] & ~0x1) | 0x20
        else:
            self.csr[4 * 1] = (self.csr[4 * 1] & ~0x21)
                
    @property
    def q_en(self):
        return True if self.ctrl_stat & 0x10 else False

    @q_en.setter
    def q_en(self, v):
        if v:
            self.csr[4 * 1] = (self.csr[4 * 1] & ~0x1) | 0x10
        else:
            self.csr[4 * 1] = (self.csr[4 * 1] & ~0x11)
            
    
    @cached_property
    def ip_id(self):
        return self.csr[0]

    @property
    def ctrl_stat(self):
        return self.csr[1 * 4]
        
    @property
    def start_offset(self):
        return self.csr[2 * 4]

    @property
    def end_offset(self):
        return self.csr[3 * 4]

    @cached_property
    def stream_depth(self):
        return self.csr[4 * 4]

    @cached_property
    def size_bytes(self):
        return self.csr[5 * 4]

    @property
    def trigger_count(self):
        return self.csr[6 * 4]

    @property
    def write_count(self):
        return self.csr[7 * 4]
    
    @cached_property
    def bytes_per_stream_word(self):
        return self.size_bytes // self.stream_depth
    
    @property
    def start_sample(self):
        return self.start_offset * self.bytes_per_stream_word // 4

    @property
    def end_sample(self):
        return (self.end_offset + 1) * self.bytes_per_stream_word // 4

    @property
    def nsamples(self):
        return self.end_sample - self.start_sample

    @command
    def status(self):
        print(f"IP id: {self.csr[4 * 0]:08x}")
        print(f"CTRLSTAT: {self.csr[4 * 1]:08x}")
        print(f"START OFFSET: {self.csr[4 * 2]:08x}")
        print(f"END OFFSET: {self.csr[4 * 3]:08x}")
        print(f"STREAM DEPTH: {self.csr[4 * 4]:08x}")
        print(f"SIZE BYTES: {self.csr[4 * 5]:08x}")
        print(f"TRIGGER COUNT: {self.csr[4 * 6]:08x}")
        print(f"WRITE COUNT: {self.csr[4 * 7]:08x}")
    
    @command
    def one_shot(self, v : bool = True):
        if v:
            self.csr[4 * 1] = (self.csr[4 * 1] & ~0x1) | 2
        else:
            self.csr[4 * 1] = self.csr[4 * 1] & ~3
    
    @command
    def trigger(self):
        self.csr[4 * 1] |= 1

    @command
    def capture(self):
        self.trigger()

        while(self.csr[4 * 1] & 3) not in [0, 1, 2]:
            time.sleep(0.001)

        return self.array
            
    @cmdproperty
    def fundamental_freq(self):
        return self.sample_rate / (self.end_sample - self.start_sample)

    def round_freq(self, f):
        return self.fundamental_freq * round(f / self.fundamental_freq)
    
    @property
    def t(self):
        return np.arange(self.nsamples, dtype=np.double) / self.sample_rate.Hz

    @property
    def T(self):
        return self.nsamples / self.sample_rate

    @property
    def f(self):
        return np.fft.fftshift(np.fft.fftfreq(self.nsamples, 1.0/self.sample_rate.Hz))

    @property
    def fft(self):
        return (self.f, np.fft.fftshift(np.fft.fft(self.array, norm="forward")))

    def decimate(self, n=2):
        return decimate(self.array, n)    

    @property
    def samples(self):
        return Samples(self.array, sample_rate=self.sample_rate)

    @samples.setter
    def samples(self, v):
        assert v.sample_rate == self.sample_rate

        if len(v) < self.nsamples:
            v = Samples.concatenate(v, Samples.zeros(self.nsamples - len(v), sample_rate=self.sample_rate))
        
        self.array = v.samples
    
    @property
    def array(self):
        if self.sample_format == IQ_SAMPLES:
            v = np.array([ self.sample_map[i] for i in range(self.start_sample, self.end_sample) ]) / 0x7FFF
            
            return v[...,0] + 1j * v[...,1]
        elif self.sample_format == REAL_SAMPLES:
            return np.array([ self.sample_map[i] for i in range(self.start_sample, self.end_sample) ]) / 0x7FFF
        else:
            raise RuntimeError("Not implemented")

    @array.setter
    def array(self, v):
        if self.sample_format == IQ_SAMPLES:
            v = v * 0x7FFF

            rearr = np.real(v).astype(int)
            imarr = np.imag(v).astype(int)

            v = zip(rearr, imarr)
            
            for i, s in enumerate(v):
                self.sample_map[i] = s
        elif self.sample_format == REAL_SAMPLES:
            v = np.array(v * 0x7FFF).astype(int)

            for i, s in enumerate(v):
                self.sample_map[i] = s

    
class SampleBufferIn(SampleBuffer):
    swap_IQ = True
    sample_rate = 4e9
    
    def __init__(self, n, **kwargs):
        assert "direction" not in kwargs
        if "sample_rate" not in kwargs:
            kwargs["sample_rate"] = GHz(4)
        super().__init__(n, direction="in", **kwargs)

class SampleBufferOut(SampleBuffer):
    swap_IQ = False
    sample_rate = 2e9
    
    def __init__(self, n, **kwargs):
        assert "direction" not in kwargs
        if "sample_rate" not in kwargs:
            kwargs["sample_rate"] = GHz(2)
        super().__init__(n, direction="out", **kwargs)
                


        
