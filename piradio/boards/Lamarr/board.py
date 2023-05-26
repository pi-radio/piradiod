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
from piradio.devices import HMC6300, HMC6301
from piradio.devices.gpiospi import GPIOSPIController
from piradio.util import Freq, MHz, GHz
from piradio.devices import LTC5594Dev
from piradio.zcu111 import zcu111

sysfs_dt_path = Path("/sys/firmware/devicetree/base")
sysfs_devices_path = Path("/sys/devices/platform")



class Lamarr(CommandObject):
    def __init__(self):
        print("Initializing Hedy Lamarr (a.k.a. SDRv3)...")
        
        # setup GPIOs
        self.children.gpio = AXI_GPIO("pl_gpio")

        self.obs_gpio = self.children.gpio.outputs[0]

        self.obs_gpio.val = 0

        sclk = self.gpio.outputs[3]
        mosi = self.gpio.outputs[2]
        miso_1v35 = self.gpio.inputs[1]
        miso_1v8 = self.gpio.inputs[30]
        
        self.spi = GPIOSPIController(sclk, mosi, miso_1v35)
        self.spi_1V8 = GPIOSPIController(sclk, mosi, miso_1v8)

        self.children.LTC5594 = [ LTC5594Dev(self.spi_1V8.get_device(self.gpio.outputs[20+i])) for i in range(8) ]
        self.children.HMC6301 = [ HMC6301(self.spi.get_device(self.gpio.outputs[4+i])) for i in range(8) ]
        self.children.HMC6300 = [ HMC6300(self.spi.get_device(self.gpio.outputs[12+i])) for i in range(8) ]        

        self.lmx_spi = self.spi.get_device(self.gpio.outputs[28])

        self.mmlo_freq = GHz(60) / 3.5
        self.children.lo_root = LMX2595Dev("LO Root", self.lmx_spi, f_src=MHz(40), A=self.mmlo_freq, B=self.NCO_freq, Apwr=0, Bpwr=15)
        
        self.tune(GHz(60))
        
        print("Programming LTC5594s...")
        for c in self.LTC5594:
            c.program()
        
        print("Programming HMC6301s...")
        for c in self.HMC6301:
            c.program()
            
        print("Programming HMC6300s...")
        for c in self.HMC6300:
            c.program()

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
    def tune(self, f: Freq):
        print("Programming clock tree and LO...")

        self.mmlo_freq = f / 3.5
        
        print(f"Frequency plan:")
        print(f"HMC LO freq: {self.mmlo_freq}")
        print(f"HMC IF freq: {self.HMC_IF_freq} RF LO Freq: {self.HMC_LO_freq} RF freq: {self.HMC_RF_freq}")
        print(f"On-board IF freq: {self.NCO_freq}")

        self.lo_root.tune(self.mmlo_freq, self.NCO_freq)

        for i, adc in enumerate(zcu111.children.rfdc.children.ADC):
            adc.nco_freq = self.NCO_freq

        for dac in zcu111.children.rfdc.children.DAC:
            dac.nco_freq = self.NCO_freq
            
        self.children.lo_root.program()
        
                
    @command
    def blank_spi(self):
        for i in range(10000):
            self.spi.shift(0)
                
    @command
    def powerdown_RX(self):
        for c in self.HMC6301:
            c.powerdown()
 
    @command
    def powerup_RX(self):
        for c in self.HMC6301:
            c.powerup()
                
    @command
    def powerdown_TX(self):
        for c in self.HMC6300:
            c.powerdown()
 
    @command
    def powerup_TX(self):
        for c in self.HMC6300:
            c.powerup()
   

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
