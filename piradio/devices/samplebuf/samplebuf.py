import time
import math
import struct
from pathlib import Path
from functools import cached_property
from threading import Timer

import numpy as np
import matplotlib.pyplot as plt

from piradio.output import output
from piradio.command import command, cmdproperty, TaskGroup
from piradio.devices.uio import UIO
from piradio.util import Freq

dt_uint32 = struct.Struct(">i")

uint32 = struct.Struct("I")
iq = struct.Struct("hh")

csr_struct = struct.Struct("iiiiii")

iq_struct = struct.Struct("hh")

# For now, the univers is IQ_SAMPLES
REAL_SAMPLES=0
IQ_SAMPLES=1

def int_to_iq(n):
    def u2s(x):
        if x & (1 << 15):
            x = -((~x & 0xFFFF) + 1)
        return x
    
    I = u2s((n >> 16) & 0xFFFF)
    Q = u2s(n & 0xFFFF)

    return (I, Q)

    return iq.unpack(uint32.pack(n))

class IQBuf:
    def plot():
        pass

class Samples:
    def __init__(self, sbuf, sample_format):
        self.sbuf = sbuf
        self._format = sample_format
       
    def __getitem__(self, n):
        s = self.sbuf._samples[n]
        
        if self._format == IQ_SAMPLES:
            if isinstance(s, list):
                return map(int_to_iq, s)
            else:
                return int_to_iq(s)
        else:
            raise RuntimeException("Not implemented")
 
    def __setitem__(self, n, v):
        if self._format == IQ_SAMPLES:
            self.sbuf._samples[n] = ((v[0] & 0xFFFF) << 16) | (v[1] & 0xFFFF) # uint32.unpack(iq.pack(*v))[0]
        else:
            raise RuntimeException("Not implemented")

    def dump(self):
        if self._format == IQ_SAMPLES:
            for i in range(self.sbuf.start_sample, self.sbuf.end_sample):
                v = self[i]
                print(f"{i}: {v}")
        else:
            raise RuntimeException("Not implemented")
                
    @property
    def format(self):
        return self._format
            
    
class SampleBuffer(UIO):
    def __init__(self, n, direction, sample_rate=2e9, sample_format=IQ_SAMPLES):
        self.direction = direction
        self.n = n
        self.sample_rate=sample_rate
        self.sample_format = sample_format
        self.task_group = TaskGroup()
        self.monitor_task = None
        self._monitor = None
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
                
        super().__init__(path, attach=True)

        self.csr = self.maps[0]
        self._samples = self.maps[1]

        self.csr.map()
        self._samples.map()
        
        self.samples = Samples(self, sample_format)
        
        assert self.ip_id == 0x5053424F, f"Invalid IP identifier {self.ip_id:x}"
        
        output.debug(f"CTRL STAT: {self.ctrl_stat}")
        output.debug(f"OFFSETS: {self.start_offset}-{self.end_offset}")
        output.debug(f"STREAM_DEPTH: {self.stream_depth}")
        output.debug(f"SIZE BYTES: {self.size_bytes}")

    def read_reg(self, n):
        return uint32.unpack(self.csr_map[4*n:4*n+4])[0]
        
    @cached_property
    def ip_id(self):
        return self.csr[0]

    @property
    def ctrl_stat(self):
        return self.csr[1]
        
    @property
    def start_offset(self):
        return self.csr[2]

    @property
    def end_offset(self):
        return self.csr[3]

    @cached_property
    def stream_depth(self):
        return self.csr[4]

    @cached_property
    def size_bytes(self):
        return self.csr[5]

    @property
    def trigger_count(self):
        return self.csr[6]

    @property
    def write_count(self):
        return self.csr[7]
    
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
        print(f"IP id: {self.csr[0]:08x}")
        print(f"CTRLSTAT: {self.csr[1]:08x}")
        print(f"START OFFSET: {self.csr[2]:08x}")
        print(f"END OFFSET: {self.csr[3]:08x}")
        print(f"STREAM DEPTH: {self.csr[4]:08x}")
        print(f"SIZE BYTES: {self.csr[5]:08x}")
        print(f"TRIGGER COUNT: {self.csr[6]:08x}")
        print(f"WRITE COUNT: {self.csr[7]:08x}")
    
    @command
    def one_shot(self, v : bool = True):
        if v:
            self.csr[1] = (self.csr[1] & ~0x1) | 2
        else:
            self.csr[1] = self.csr[1] & ~3
    
    @command
    def trigger(self):
        self.csr[1] |= 1

    @command
    def save(self, name : str):
        self.capture()

        with open(name, "w") as f:
            for r in self.array:
                print(r, file=f)
        
    @command
    def plot(self):
        if self._monitor is None:
            from piradio.monitor import get_monitor
            self._monitor = get_monitor()

        self._monitor.send(self.array)
        

    @command
    def plot_local(self):
        pass
        
    @command
    def capture(self):
        self.trigger()

        while (self.csr[1] & 3) not in [ 0, 1, 2 ]:
            time.sleep(0.001)

    def monitor_timeout(self):
        self.capture()
        self.plot()
            
    @command
    def monitor(self):
        self.one_shot(True)
        self.monitor_task = self.task_group.create_task(1, self.monitor_timeout)
        
        
    @command
    def dump(self):
        self.samples.dump()

    @cmdproperty
    def fundamental_freq(self):
        return self.sample_rate / (self.end_sample - self.start_sample)

    @property
    def t(self):
        return np.arange(0, self.nsamples) / self.sample_rate

    @property
    def T(self):
        return self.nsamples / self.sample_rate
    
    @command
    def fill_sine(self, freq: Freq, phase : float = 0):
        if self.samples._format == IQ_SAMPLES:
            phase_advance = 2 * math.pi * freq / self.sample_rate
            phi = phase

            v = np.arange(0, self.nsamples) * phase_advance + phase
            v = (np.sin(v) - 1.0j * np.cos(v)) * 0x7FFF
            
            for i, x in zip(range(self.start_sample, self.end_sample), v):
                self.samples[i] = (int(x.real), int(x.imag))
        else:
            raise RuntimeException("Not implemented")

    @command
    def fill_chirp(self, freqA: Freq, freqB: Freq, phase : float = 0, N : int=1):
        if self.samples._format == IQ_SAMPLES:
            T = self.T / N
            
            c = (freqB - freqA) / T        
            t = np.arange(0, self.nsamples / N) / self.sample_rate

            t = np.tile(t, N)
            
            phi = phase + 2 * np.pi * (t * c + freqA) * t
            
            v = (np.sin(phi) - 1.0j * np.cos(phi)) * 0x7FFF
            
            for i, x in zip(range(self.start_sample, self.end_sample), v):
                self.samples[i] = (int(x.real), int(x.imag))
        else:
            raise RuntimeException("Not implemented")

        
    def fill_Zadoff_Chu(self, Nzc : int, u : int, q : int):
        c_f = Nzc & 1

        a = np.arange(0, Nzc)

        seq = 0x7FFF * np.exp(-1.0j * np.pi * u * a * (a + c_f + 2 * q) / Nzc)

        print(seq)

        for i, v in enumerate(seq):
            self.samples[self.start_sample + i] = (int(v.real), int(v.imag))
        
        for i in range(self.start_sample + Nzc, self.end_sample):
            self.samples[i] = (0,0)

    fill_zc = fill_Zadoff_Chu
            
    @property
    def array(self):
        if self.sample_format == IQ_SAMPLES:
            v = np.array([ self.samples[i] for i in range(self.start_sample, self.end_sample) ]) / 0x7FFF
            
            return v[...,0] + 1j * v[...,1]
        else:
            raise RuntimeException("Not implemented")
        
            
            
    
class SampleBufferIn(SampleBuffer):
    def __init__(self, n, **kwargs):
        assert "direction" not in kwargs
        super().__init__(n, direction="in", **kwargs)

class SampleBufferOut(SampleBuffer):
    def __init__(self, n, **kwargs):
        assert "direction" not in kwargs
        super().__init__(n, direction="out", **kwargs)

