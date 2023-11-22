import time

import numpy as np
from piradio.output import output
from .registers import attach_registers, set_bits, clear_bits, modify_bits
from .beamforming import Beamformer
from .BFM06010 import TXWeights

class TX(Beamformer):
    def __init__(self, eder):
        super().__init__(eder, TXWeights)
        self._omni = True

        self._bb_bias = 1
        self._bf_gain = 0
        self._rf_gain = 0
        self._bb_gain = 0
        self._bb_I_gain = 0
        self._bb_Q_gain = 0
        
    @property
    def rx(self):
        return self.eder.rx

    @property
    def bb_bias(self):
        return self._bb_bias

    @bb_bias.setter
    def bb_bias(self, v):
        if v:
            if self._bb_bias:
                return
            self._bb_bias = 1
        else:
            if not self._bb_bias:
                return
            self._bb_bias = 0

        if self._bb_bias:
            self.regs.tx_ctrl = set_bits(0x8)
        else:
            self.regs.tx_ctrl = clear_bits(0x8)
    
    @property
    def bb_gain(self):
        if self._bb_gain == 0:
            return 0

        if self._bb_gain == 1 or self._bb_gain == 2:
            return 6 if self._bb_bias else 3.5

        if self._bb_gain == 3:
            return 9.5 if self._bb_bias else 6

        raise RuntimeError("Invalid _bb_bias")

    @bb_gain.setter
    def bb_gain(self, gain):
        assert gain in [ 0, 3.5, 6, 9.5 ]
        if gain == 9.5:
            self.bb_bias = 1
            self._bb_gain = 3
        elif gain == 6:
            if self.bb_bias:
                self._bb_gain = 2
            else:
                self._bb_gain = 3
        elif gain == 3.5:
            self.bb_bias = 0
            self._bb_gain = 2
        elif gain == 0:
            self._bb_gain = 0

        self.regs.tx_bb_gain = self._bb_gain

    @property
    def bb_I_gain(self):
        return 6 * self._bb_I_gain / 15
    
    @property
    def bb_Q_gain(self):
        return 6 * self._bb_Q_gain / 15

    @bb_I_gain.setter
    def bb_I_gain(self, gain):
        assert gain >=0 and gain <= 6

        self._bb_I_gain = int(15 * gain / 6)

        self.regs.tx_bb_iq_gain = self._bb_I_gain | (self._bb_Q_gain << 4)

    @bb_Q_gain.setter
    def bb_Q_gain(self, gain):
        assert gain >=0 and gain <= 6

        self._bb_Q_gain = int(15 * gain / 6)

        self.regs.tx_bb_iq_gain = self._bb_I_gain | (self._bb_Q_gain << 4)
    
    @property
    def rf_gain(self):
        return self._rf_gain

    @rf_gain.setter
    def rf_gain(self, gain):
        assert gain >= 0 and gain <= 15

        self._rf_gain = int(gain)

        self.regs.tx_bfrf_gain = (self._bf_gain << 4) | self._rf_gain

    @property
    def bf_gain(self):
        return self._bf_gain

    @bf_gain.setter
    def bf_gain(self, gain):
        assert gain >= 0 and gain <= 15

        self._bf_gain = int(gain)

        self.regs.tx_bfrf_gain = (self._bf_gain << 4) | self._rf_gain
        
    @property
    def gain(self):
        return self.bb_gain + (self.bb_I_gain + self.bb_Q_gain) / 2 + self.bf_gain + self.rf_gain

    @property
    def swap_iq(self):
        return True if self.regs.tx_ctrl & 0x02 else False

    @swap_iq.setter
    def swap_iq(self, v):
        if v:
            self.regs.tx_ctrl = set_bits(0x02)
        else:
            self.regs.tx_ctrl = clear_bits(0x02)
    
    def startup(self):
        self.eder.regs.trx_tx_on = 0x1FFFFF
        self.eder.regs.trx_tx_off = 0x000000

        if self.eder.mmf:
            self.eder.regs.bias_tx = 0x96AA
        else:
            self.eder.regs.bias_tx = 0xAEAA

        self.regs.bias_ctrl = set_bits(0x40)
        self.regs.bias_lo = set_bits(0xA)

        self.regs.tx_ctrl = 0x10

        self.bb_gain = 0
        self.bb_I_gain = 0
        self.bb_Q_gain = 0
        self.rf_gain = 0
        self.bf_gain = 0
        
        #| (self._bb_bias << 3)
        #self.regs.tx_ctrl = 0x08
        #self.regs.tx_bb_gain = 0x00
        #self.regs.tx_bb_phase = 0x00
        #self.regs.tx_bb_iq_gain = 0xFF
        #self.regs.tx_bfrf_gain = 0xFF

        #self.calibrate()

        if "tx_bb_i_dco" in self.config and "tx_bb_q_dco" in self.config:
            self.regs.tx_bb_i_dco = self.config["tx_bb_i_dco"]
            self.regs.tx_bb_q_dco = self.config["tx_bb_q_dco"]
            
        output.info("TX startup complete")
        self.omni = True
        self.update_beamformer()


    def alc_init(self):
        self.regs.tx_alc_pdet_lo_th = 0x80
        self.regs.tx_alc_pdet_hi_offs_th = 0x04
        self.regs.tx_alc_ctrl = alc_ctrl
        self.regs.tx_alc_loop_cnt = 0x00
        self.regs.tx_alc_start_delay = self.dig_pll.cycles(2)   # 2 us
        self.regs.tx_alc_meas_delay = self.dig_pll.cycles(1)   # 1 us
        self.regs.tx_alc_bfrf_gain_max = 0xff
        self.regs.tx_alc_bfrf_gain_min = 0x00
        self.regs.tx_alc_step_max = 0x13
        self.regs.tx_bf_pdet_mux = set_bits(0x80)


    def alc_enable(self):
        self.regs.tx_alc_ctrl = set_bits(0x01)

    def alc_disable(self):
        self.regs.tx_alc_ctrl = clear_bits(0x03)


    def alc_start(self):
        if (self.regs.tx_alc_ctrl & 0x01) == 0x01:
            self.regs.tx_alc_ctrl = toggle_bits(0x02)
        else:
            self.regs.tx_alc_ctrl = clear_bits(0x03)
            self.regs.tx_alc_ctrl = set_bits(0x03)

    def alc_stop(self):
        if (self.regs.tx_alc_ctrl & 0x01) == 0x01:
            self.regs.tx_alc_ctrl = clear_bits(0x03)
            self.regs.tx_alc_ctrl = set_bits(0x01)
        else:
            self.regs.tx_alc_ctrl = clear_bits(0x03)

    def pdet_dump(self):
        #bist_amux_ctrl = self.regs.bist_amux_ctrl
        #tx_bf_pdet_mux = self.regs.tx_bf_pdet_mux

        adc = self.eder.adc
        
        output.print("Detector power:")
        
        def get_pdet(i):
            return (i, adc.acquire(adc.pdet[i]).mean, adc.acquire(adc.env_pdet[i]).mean)
        
        pdet_vals = [ get_pdet(i) for i in range(0, 16) ]

        for i, power, env_power in pdet_vals:
            output.print(f"{i}: {power} {env_power}")

            
    def ready(self):
        pass

    def loopback(self):
        #self.regs.trx_tx_on = 0x070000;
        self.regs.trx_tx_on = 0x1F0000;
        self.regs.tx_ctrl = set_bits(0x40)

    def loopback_off(self):
        self.regs.trx_tx_on = 0x1FFFFF;
        self.regs.tx_ctrl = clear_bits(0x40)

        
    @property
    def beamweights_reg(self):
        return self.regs.bf_tx_awv

    @property
    def bf_idx_reg(self):
        return self.regs.bf_tx_awv_ptr

    @bf_idx_reg.setter
    def bf_idx_reg(self, v):
        self.regs.bf_tx_awv_ptr = v
        
    def calibrate_tx_gain(self):
        pass
    
    def calibrate(self):
        output.info("Starting TX calibration...")
              
        with self.regs.push_regs():
            self.regs.rx_gain_ctrl_bb1 = 0xFF
            self.regs.rx_gain_ctrl_bb2 = 0xFF
            self.regs.rx_gain_ctrl_bb3 = 0xFF
            self.regs.rx_gain_ctrl_bfrf = 0x0F

            self.regs.tx_ctrl = clear_bits(0x08)            
            self.regs.tx_bb_gain = 0x3
            self.regs.tx_bb_iq_gain = 0xFF
            self.regs.tx_bfrf_gain = 0x0F
                        
            self.regs.trx_rx_on = 0x1F0000
            self.regs.trx_tx_on = 0x1F0000

            # Manually switch to loopback
            self.regs.trx_ctrl = set_bits(0x3)
            self.regs.tx_ctrl = set_bits(0x40)

            iqs = [ I + 1.0j * Q for I in [ 0x00, 0x7F, 0x40 ] for Q in [ 0x00, 0x7F, 0x40 ] ]            

            with self.regs.push_regs():
                self.regs.tx_ctrl = clear_bits(0x40)
                self.regs.trx_ctrl = clear_bits(0x02)
                
                time.sleep(0.01)
            
                rx_meas = [ self.rx.measure_dco(l2samp=10).dco_diff for i in range(100) ]

                print(np.mean(rx_meas))
                print(np.std(np.real(rx_meas)), np.std(np.imag(rx_meas)))
                print(np.max(np.real(rx_meas)) - np.min(np.real(rx_meas)),
                      np.max(np.imag(rx_meas)) - np.min(np.imag(rx_meas)))
            
                rx_dco_diff = rx_meas[0]

            print(f"DCO: {rx_dco_diff}")
            
            def measure_loopback_dco(iq):
                with self.regs.push_regs():
                    self.regs.tx_ctrl = clear_bits(0x40)
                    self.regs.trx_ctrl = clear_bits(0x02)

                    time.sleep(0.01)

                    rx_dco_diff = self.rx.measure_dco(l2samp=5).dco_diff

                time.sleep(0.01)
                    
                self.regs.tx_bb_i_dco = int(np.real(iq))
                self.regs.tx_bb_q_dco = int(np.imag(iq))
                
                dco_diff = self.rx.measure_dco(l2samp=10).dco_diff - rx_dco_diff

                print(f"I: {np.real(iq)} Q: {np.imag(iq)} rx_dco_diff: {rx_dco_diff} diff: {dco_diff}")
                return dco_diff

            
            def sqlim(v, e):
                return np.abs(np.real(v)) < e and np.abs(np.imag(v)) < e

            def sqclip(v, c):
                s = v - c

                return np.clip(round(np.real(s)), 0, 0x7F) + 1.0j * np.clip(round(np.imag(s)), 0x0, 0x7F)
                            
            while True:
                dcos = [ measure_loopback_dco(iq) for iq in iqs ]

                g = np.gradient(dcos, iqs)

                for x, d, cg in zip(iqs, dcos, g):
                    print(f"Trial: {np.real(x)} {np.imag(x)}: {d} {cg:2f}")
                
                if np.max(np.abs(dcos)) < 50:
                    break
                
                if sqlim(dcos[-1]/g[-1], 0x40):
                    break

                output.info(f"TX calibration reducing gain: {dcos[-1]/g[-1]}")
                
                if self.regs.rx_gain_ctrl_bfrf > 2:
                    self.regs.rx_gain_ctrl_bfrf -= 2
                elif self.regs.rx_gain_ctrl_bfrf > 0:
                    self.regs.rx_gain_ctrl_bfrf -= 1
                elif self.regs.tx_bfrf_gain > 3:
                    self.regs.tx_bfrf_gain -= 3
                elif self.regs.tx_bfrf_gain > 0:
                    self.regs.tx_bfrf_gain -= 1
                else:
                    raise RuntimeError("Unable to find DCO solution")

                self.regs.tx_ctrl = clear_bits(0x40)

                time.sleep(0.01)
                
                rx_dco_diff = self.rx.measure_dco(l2samp=5).dco_diff

                self.regs.tx_ctrl = set_bits(0x40)


            i = 20
            
            while np.abs(dcos[-1]) > 4 and g[-1] > 1/64:                
                c = dcos[-1]/g[-1]

                print(f"V: {iqs[-1]} c: {c}")

                v = sqclip(iqs[-1], c)

                if v == iqs[-1]:
                    break;
                
                if i == 0:
                    raise RuntimeError("TX calibration was unable to converge")
                
                iqs.append(v)
                
                dcos.append(measure_loopback_dco(iqs[-1]))

                g = np.gradient(dcos, iqs)

                output.info(f"TX DCO New solution: {iqs[-1]} {dcos[-1]}")

                i -= 1

        output.info(f"TX DCO final result: {iqs[-1]} {dcos[-1]}")

        self.regs.tx_bb_i_dco = int(np.real(iqs[-1]))
        self.regs.tx_bb_q_dco = int(np.imag(iqs[-1]))

        self.config["tx_bb_i_dco"] = self.regs.tx_bb_i_dco
        self.config["tx_bb_q_dco"] = self.regs.tx_bb_q_dco
        

                
                
