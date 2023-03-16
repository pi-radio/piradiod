import os
import sys
import time
import traceback
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as signal
from pathlib import Path

from piradio.command import CommandObject, command
from piradio.output import output
from piradio.devices import SysFS, SPIDev
from piradio.devices import Renesas_8T49N240, LMX2595Dev
from piradio.devices import AXI_GPIO
from piradio.devices import SampleBufferIn, SampleBufferOut
from piradio.devices import Trigger
from piradio.devices import HMC6300, HMC6301
from piradio.devices.gpiospi import GPIOSPIController
from piradio.util import MHz, GHz
from piradio.devices import LTC5594Dev
from piradio.zcu111 import zcu111

sysfs_dt_path = Path("/sys/firmware/devicetree/base")
sysfs_devices_path = Path("/sys/devices/platform")



class Lamarr(CommandObject):
    def __init__(self):
        print("Initializing C.V. Raman (a.k.a. SDRv2)...")

        self.children.input_samples = [ SampleBufferIn(i) for i in range(8) ]
        self.children.output_samples = [ SampleBufferOut(i) for i in range(8) ]

        
        # setup GPIOs
        self.children.gpio = AXI_GPIO("pl_gpio")

        self.obs_gpio = self.children.gpio[0]

        self.obs_gpio.dir = "out"
        self.obs_gpio.val = 0
        
        for i in range(4, 29):
            self.children.gpio[i].dir = "out"
            self.children.gpio[i].val = 1

        spi = GPIOSPIController(self.children.gpio[3], self.children.gpio[2], self.children.gpio[1])
        spi_1V8 = GPIOSPIController(self.children.gpio[3], self.children.gpio[2], self.children.gpio[30])

        lmx_spi = spi.get_device(self.children.gpio[28])

        print("Programming clock tree and LO...")

        center_frequency = GHz(60)
        
        self.mmlo_freq = center_frequency / 3.5

        print(f"Frequency plan:")
        print(f"HMC LO freq: {self.mmlo_freq}")
        print(f"HMC IF freq: {self.HMC_IF_freq} RF LO Freq: {self.HMC_LO_freq} RF freq: {self.HMC_RF_freq}")
        print(f"On-board IF freq: {self.NCO_freq}")
        
        self.children.lo_root = LMX2595Dev("LO Root", lmx_spi, f_src=MHz(40), A=self.mmlo_freq, B=self.NCO_freq, Apwr=0, Bpwr=25)

        for i, adc in enumerate(zcu111.children.rfdc.children.ADC):
            adc.nco_freq = self.NCO_freq

        for dac in zcu111.children.rfdc.children.DAC:
            dac.nco_freq = self.NCO_freq
            
        self.children.lo_root.program()

        
        print("Programming LTC5594s...")
        self.children.LTC5594 = [ LTC5594Dev(spi_1V8.get_device(self.children.gpio[20+i])) for i in range(8) ]
        

        
        print("Programming HMC6301s...")
        self.children.HMC6301 = [ HMC6301(spi, self.children.gpio[4+i]) for i in range(8) ]
        print("Programming HMC6300s...")
        self.children.HMC6300 = [ HMC6300(spi, self.children.gpio[12+i]) for i in range(8) ]
        
        
        self.children.trigger = Trigger()

    

    @property
    def HMC_IF_freq(self):
        return self.mmlo_freq / 2

    @property
    def HMC_LO_freq(self):
        return self.mmlo_freq * 3

    @property
    def HMC_RF_freq(self):
        return self.HMC_LO_freq + self.HMC_IF_freq

    @property
    def NCO_freq(self):
        return self.mmlo_freq / 16
    
    def all_radios(self):
        for r in self.children.radios:
            if r is not None:
                yield r

    @command
    def silence(self):
        for i in range(8):
            self.children.output_samples[0].one_shot(True)
                    
    @command
    def tone_test(self):
        f = self.children.output_samples[0].fundamental_freq * 128

        print(f"Output frequency: {f}")

        for i in range(1):
            self.children.output_samples[i].fill_sine(f)                
            #self.children.output_samples[0].fill_Zadoff_Chu(512, 1, 1)
            self.children.output_samples[0].one_shot(False)
            
        self.children.trigger.trigger()

        
        os.fill_sine(os.fundamental_freq * 32)

        os.one_shot(False)

        os.trigger()

    @command
    def radar_test(self):
        os = self.children.output_samples[0]
        
        N = 4
        fA = os.fundamental_freq * 8
        fB = os.fundamental_freq * 128

        t = os.t 
        
        os.fill_chirp(fA, fB, N=N)

        self.children.input_samples[0].one_shot(True)
        os.one_shot(True)
        self.children.trigger.trigger()

        self.children.input_samples[0].plot()

        ina = self.children.input_samples[0].array
        outa = os.array

        sample_rate = os.sample_rate

        
        b, a = signal.butter(5, 256/4096)
        zi = signal.lfilter_zi(b, a)
        
        fina, _ = signal.lfilter(b, a, ina, zi=zi*ina[0])

        mix = fina * outa

        fft = np.fft.fftshift(np.fft.fft(mix))

        f = np.fft.fftshift(np.fft.fftfreq(len(fft))) * sample_rate
        
        fig, axs = plt.subplots(4, 1)

        axs[0].plot(t, outa)
        
        axs[1].plot(t, ina)
        axs[1].plot(t, fina)

        axs[2].plot(mix)

        axs[3].plot(f, np.abs(fft))

        c = N * (fB - fA) / os.T 
        
        max_idx = np.argmax(np.abs(fft))

        fmax = f[max_idx] 

        tp = fmax / (2 * c)

        print(f"Max freq: {fmax} t: {tp*1e9}ns")
        
        plt.show()

    @command
    def sounder_test(self):
        Nzc = 512
        
        os = self.children.output_samples[1]
        
        os.fill_Zadoff_Chu(Nzc, 1, 1)

        self.children.trigger.trigger()
        
        self.children.input_samples[0].plot()

        zc = os.array[:Nzc]

        corr = np.correlate(self.children.input_samples[0].array, zc)

        fig, axs = plt.subplots(nrows=2, ncols=1)
        
        axs[0].plot(os.t[:len(corr)], np.abs(corr))
        axs[1].plot(os.t[:len(corr)], np.angle(corr))

        plt.show()

    @command
    def obs_on(self):
        self.obs_gpio.val = 1

    @command
    def obs_off(self):
        self.obs_gpio.val = 0
