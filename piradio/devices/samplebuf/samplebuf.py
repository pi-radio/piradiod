import math
import struct
from pathlib import Path
from functools import cached_property
from multiprocessing import Process

import numpy as np
import matplotlib.pyplot as plt

from piradio.output import output
from piradio.command import command
from piradio.devices.uio import UIO

dt_uint32 = struct.Struct(">i")

uint32 = struct.Struct("I")
iq = struct.Struct("hh")

csr_struct = struct.Struct("iiiiii")

iq_struct = struct.Struct("hh")

# For now, the univers is IQ_SAMPLES
REAL_SAMPLES=0
IQ_SAMPLES=1

def int_to_iq(n):
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
            self.sbuf._samples[n] = uint32.unpack(iq.pack(*v))[0]
        else:
            raise RuntimeException("Not implemented")

    def dump(self):
        if self._format == IQ_SAMPLES:
            for i in range(self.sbuf.start_sample, self.sbuf.end_sample):
                v = self[i]
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
            self.csr[1] |= 2
        else:
            self.csr[1] &= ~2
    
    @command
    def trigger(self):
        x = self.csr[1] | 3        
        self.csr[1] = 0xFFFFFFFF

    @command
    def capture(self):
        self.trigger()
        self.plot()
        
    @command
    def fill_sine(self, freq: float, phase : float = 0):
        if self.samples._format == IQ_SAMPLES:
            phase_advance = 2 * math.pi * freq / self.sample_rate
            phi = phase

            v = np.arange(0, self.nsamples) * phase_advance + phase
            v = (np.sin(v) - 1.0j * np.cos(v)) * 0x7FFF
            
            for i, x in zip(range(self.start_sample, self.end_sample), v):
                self.samples[i] = (int(x.real), int(x.imag))
        else:
            raise RuntimeException("Not implemented")

    @property
    def array(self):
        if self.sample_format == IQ_SAMPLES:
            v = np.array([ self.samples[i] for i in range(self.start_sample, self.end_sample) ]) / 0x7FFF

            v = v[...,0] + 1j * v[...,1]
            
            return v
        else:
            raise RuntimeException("Not implemented")
        
    @command
    def plot(self):
        if self.sample_format == IQ_SAMPLES:
            def plot_iq(samples, sample_rate):
                N = len(samples)
                
                fig, axs = plt.subplots(2, 1)

                t = np.arange(0, N) / sample_rate
                
                axs[0].plot(t, np.real(samples), t, np.imag(samples))

                df = sample_rate / N
                
                fft = np.fft.fftshift(np.fft.fft(samples))
                f = np.fft.fftshift(np.fft.fftfreq(N)) * sample_rate

                dB = np.nan_to_num(10 * np.log10(np.abs(fft) / N), nan=-100, posinf=100, neginf=-100)
                
                axs[1].plot(f, dB)

                plt.show()

            p = Process(target=plot_iq, args=(self.array, self.sample_rate))
            p.daemon = True
            p.start()

    @command
    def monitor(self):
        pass
            
    
class SampleBufferIn(SampleBuffer):
    def __init__(self, n, **kwargs):
        assert "direction" not in kwargs
        super().__init__(n, direction="in", **kwargs)

class SampleBufferOut(SampleBuffer):
    def __init__(self, n, **kwargs):
        assert "direction" not in kwargs
        super().__init__(n, direction="out", **kwargs)

