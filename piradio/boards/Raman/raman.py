import os
import sys
import time
import traceback
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as signal
from pathlib import Path

from piradio.command import CommandObject, command, cmdproperty
from piradio.output import output
from piradio.devices import SysFS, SPIDev
from piradio.devices import Renesas_8T49N240, LMX2595Dev
from piradio.devices import AXI_GPIO
from piradio.devices import Trigger
from piradio.devices.sivers import Eder, EderChipNotFoundError
from piradio.util import MHz
from piradio import zcu111

sysfs_dt_path = Path("/sys/firmware/devicetree/base")
sysfs_devices_path = Path("/sys/devices/platform")


class Raman(CommandObject):
    def __init__(self):
        print("Initializing C.V. Raman (a.k.a. SDRv2)...")

        self._NCO_freq = MHz(1035)
        
        # setup GPIOs
        self.children.gpio = AXI_GPIO("pl_gpio")

        print("Resetting board...")

        self.children.reset = self.gpio.outputs[0]

        self.reset.val = 0
        time.sleep(0.25)
        self.reset.val = 1
        time.sleep(0.25)

        print("Programming clock tree and LO...")
        
        self.children.clk_root = Renesas_8T49N240()

        self.clk_root.program()
        
        self.children.lo_root = LMX2595Dev("LO Root", SPIDev(2, 24), f_src=MHz(45), A=self.NCO_freq, B=self.NCO_freq, Apwr=20, Bpwr=20)

        for i, adc in enumerate(zcu111.rfdc.ADC):
            print(f"Cur ADC {i} NCO Freq: {adc.nco_freq}")
            adc.nco_freq = self.NCO_freq

        for i, dac in enumerate(zcu111.rfdc.DAC):
            print(f"Cur DAC {i} NCO Freq: {dac.nco_freq}")
            dac.nco_freq = self.NCO_freq
            
        self.lo_root.program()

        self.children.radios = [ None ] * 8
        
        print("Detecting radios...")

        self.detect_radios()
        
    @command
    def detect_radios(self):
        for card in range(4):
            for radio in range(2):
                n =  2*card + radio

                if self.children.radios[n] is not None:
                    continue
                
                try:
                    eder = Eder(SPIDev(2, 6 * card + 2 * radio + 1, mode=0), n)
                    print(f"Found radio {n}")
                    self.children.radios[n] = eder
                    eder.INIT()
                    eder.freq = 60e9
                except EderChipNotFoundError:
                    pass
                except Exception as e:
                    print(f"Failed to detect radio {2 * card + radio}")
                    traceback.print_exc()
                    
    def all_radios(self):
        for r in self.children.radios:
            if r is not None:
                yield r

    @cmdproperty
    def NCO_freq(self):
        return self._NCO_freq

    @NCO_freq.setter
    def NCO_freq(self, v):
        print(f"Changing NCO freq to {v}")
        self._NCO_freq = v
        self.children.lo_root.tune(self._NCO_freq, self._NCO_freq)

        for i, adc in enumerate(zcu111.children.rfdc.children.ADC):
            adc.nco_freq = self._NCO_freq

        for dac in zcu111.children.rfdc.children.DAC:
            dac.nco_freq = self._NCO_freq

    @command
    def listen(self, n : int):
        self.children.radios[n].RX()
        self.children.input_samples[n].monitor
            
    @command
    def TX_test(self):
        for r in self.all_radios():
            r.INIT()
            r.freq = 60e9
            r.SX()
            
        while True:
            for r in self.all_radios():
                r.TX()

            time.sleep(5)

            for r in self.all_radios():
                r.RX()

    @command
    def loopback_test(self):
        self.children.radios[0].LOOP()

        f = self.children.output_samples[0].fundamental_freq * 256

        self.children.output_samples[0].fill_sine(f)
        
        self.children.output_samples[0].one_shot(False)
        self.children.output_samples[0].trigger()

    @command
    def send_tone(self, tx_radio : int):
        self.children.radios[tx_radio].TX()

        os = self.children.output_samples[tx_radio];

        os.fill_sine(os.fundamental_freq * 256)

        os.one_shot(False)
        os.trigger()
        
    @command
    def radar_test(self):
        self.children.radios[0].RX()

        self.children.radios[1].TX()

        os = self.children.output_samples[1]
        
        #self.children.radios[0].rx.set_gain(((0, 0), (3, 3), (3, 3), (15, 15)))
        
        N = 4
        fA = os.fundamental_freq * 8
        fB = os.fundamental_freq * 128

        t = os.t 
        
        os.fill_chirp(fA, fB, N=N)

        self.children.input_samples[0].one_shot(True)
        os.one_shot(True)
        self.children.trigger.trigger()

        self.children.input_samples[0].plot()

        self.children.radios[0].SX()
        self.children.radios[1].SX()

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
        self.children.radios[0].RX()

        self.children.radios[1].TX()

        Nzc = 512
        
        os = self.children.output_samples[1]
        
        os.fill_Zadoff_Chu(Nzc, 1, 1)

        self.children.trigger.trigger()
        
        self.children.input_samples[0].plot()
        
        self.children.radios[0].SX()
        self.children.radios[1].SX()

        zc = os.array[:Nzc]

        corr = np.correlate(self.children.input_samples[0].array, zc)

        fig, axs = plt.subplots(nrows=2, ncols=1)
        
        axs[0].plot(os.t[:len(corr)], np.abs(corr))
        axs[1].plot(os.t[:len(corr)], np.angle(corr))

        plt.show()
