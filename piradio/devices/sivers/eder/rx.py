import numpy as np

from piradio.output import output
from piradio.devices.sivers.eder.registers import attach_registers, set_bits, clear_bits
from piradio.devices.sivers.eder.child import EderChild
from .iq import RX_IQ, measure_IQ 
from .beamforming import Beamformer
from .BFM06010 import RXWeights

class RXChannel(EderChild):
    def __init__(self, rx):
        self.rx = rx
        super().__init__(rx.eder)    

    def drv_cal(self):
        found = False
        
        for dco_sign in [ 0, (1 << 5) ]:
            self.drv_offset = dco_sign
            v0 = self.dco_diff
            self.drv_offset = (dco_sign) | 0x1F
            v1 = self.dco_diff

            if np.sign(v0) != np.sign(v1):
                found = True
                break

        if not found:
            raise RuntimeError("RX DRV DCO calibration failed")

        self.start_dco = 0
        self.end_dco = 0x1F

        self.drv_offset = (dco_sign) | self.start_dco
        self.start_diff = self.dco
        
        self.drv_offset = dco_sign | self.end_dco
        self.end_diff = self.dco

        while abs(self.end_dco - self.start_dco) > 1:
            mean_dco = int(round((self.start_dco + self.end_dco) / 2))
            self.drv_offset = dco_sign | mean_dco
            diff = self.dco

            if np.sign(diff) == np.sign(self.start_diff):
                self.start_dco = mean_dco
                self.start_diff = diff
            if np.sign(diff) == np.sign(self.end_diff):
                self.end_dco = mean_dco
                self.end_diff = diff
            elif diff == 0:
                return
            else:
                raise RuntimeError("DCO search broken")

        if abs(self.end_diff) < abs(self.start_diff):
            self.drv_offset = dco_sign | self.end_dco
        else:
            self.drv_offset = dco_sign | self.start_dco


    def dco_cal(self):
        found = False

        for mult in [ (i << 12) for i in range(4) ]:
            if found:
                break
            
            for shift in [ (i << 8) for i in range(3) ]:
                self.dco_reg = mult | shift
                v0 = self.dco_diff
                self.dco_reg = mult | shift | 0x7F
                v1 = self.dco_diff

                if np.sign(v0) != np.sign(v1):
                    found = True
                    break

        if not found:
            raise RuntimeError("RX DCO calibration failed")

        self.start_dco = 0
        self.end_dco = 0x7F

        self.dco_reg = mult | shift | self.start_dco
        self.start_diff = self.dco
        
        self.drv_reg = mult | shift | self.end_dco
        self.end_diff = self.dco

        while abs(self.end_dco - self.start_dco) > 1:
            mean_dco = int(round((self.start_dco + self.end_dco) / 2))
            self.dco_reg = mult | shift | mean_dco
            diff = self.dco

            if np.sign(diff) == np.sign(self.start_diff):
                self.start_dco = mean_dco
                self.start_diff = diff
            if np.sign(diff) == np.sign(self.end_diff):
                self.end_dco = mean_dco
                self.end_diff = diff
            elif diff == 0:
                return
            else:
                raise RuntimeError("DCO search broken")

        if abs(self.end_diff) < abs(self.start_diff):
            self.dco_reg = mult | shift | self.end_dco
        else:
            self.dco_reg = mult | shift | self.start_dco


    @property
    def dco(self):
        return self.meas.dco

    @property
    def dco_diff(self):
        return self.meas.dco_diff
        
class RX_I(RXChannel):
    @property
    def dco_reg(self):
        return self.regs.rx_bb_i_dco

    @dco_reg.setter
    def dco_reg(self, v):
        self.regs.rx_bb_i_dco = v
    
    @property
    def drv_offset(self):
        return (self.regs.rx_drv_dco >> 14) & 0x3F

    @drv_offset.setter
    def drv_offset(self, v):
        self.regs.rx_drv_dco = clear_bits(0x3F << 14)
        self.regs.rx_drv_dco = set_bits((v & 0x3F) << 14)

    @property
    def meas(self):
        return self.rx.measure_dco().I
        
class RX_Q(RXChannel):
    @property
    def dco_reg(self):
        return self.regs.rx_bb_q_dco

    @dco_reg.setter
    def dco_reg(self, v):
        self.regs.rx_bb_q_dco = v

    @property
    def drv_offset(self):
        return (self.regs.rx_drv_dco >> 8) & 0x3F

    @drv_offset.setter
    def drv_offset(self, v):
        self.regs.rx_drv_dco = clear_bits(0x3F << 8)
        self.regs.rx_drv_dco = set_bits((v & 0x3F) << 8)

    @property
    def meas(self):
        return self.rx.measure_dco().Q
        
class RX(Beamformer):
    
    def __init__(self, eder):
        super().__init__(eder, RXWeights)
        self._freq = 0
        self._omni = True

        self.I = RX_I(self)
        self.Q = RX_Q(self)
        
    @property
    def regs(self):
        return self.eder.regs
        
    def startup(self):
        self.regs.trx_rx_on = 0x1FFFFF

        if self.eder.mmf:
            self.regs.bias_rx = 0xAA9
        else:
            self.regs.bias_rx = 0xAAA

        self.regs.bias_ctrl = set_bits(0x7F)
        self.regs.bias_lo = set_bits(0x22)

        self.regs.rx_bb_biastrim = 0x00
        self.regs.rx_gain_ctrl_mode = 0x13
        self.regs.rx_dco_en = 0x01
        self.regs.rx_gain_ctrl_bb1 = 0x77
        self.regs.rx_gain_ctrl_bb2 = 0x11
        self.regs.rx_gain_ctrl_bb3 = 0x77
        self.regs.rx_gain_ctrl_bfrf = 0x66

        output.info("RX calibrating baseband")

        self.regs.trx_ctrl = 0
        self.regs.trx_rx_on = 0x1E0000
        self.regs.trx_rx_off = 0x1E0000
        self.regs.rx_dco_en = 0x01
        self.regs.rx_bb_i_dco = 0x40
        self.regs.rx_bb_q_dco = 0x40

        gain = ((0,0),0x11,0x11,0x77)
        
        #bfrf_gain = self.regs.rx_gain_ctrl_bfrf

        self.regs.rx_gain_ctrl_bfrf = (gain[0][0] << 4) | gain[0][1]
        self.regs.rx_gain_ctrl_bb1 = 0x11
        self.regs.rx_gain_ctrl_bb2 = 0x11
        self.regs.rx_gain_ctrl_bb3 = 0x77
                
        self.I.drv_cal()
        self.Q.drv_cal()

        self.regs.trx_ctrl = 0x1
        self.lna_state = False

        self.I.dco_cal()
        self.Q.dco_cal()

        
        ## Stupid SIVERS code restores registers here, which should be wholly unnecessary
        
        output.info("RX startup complete")
        self.update_beamformer()

    def ready(self):
        # Go ahead and turn on the LNA
        self.lna_state = True

        
    @property
    def lna_state(self):
        if self.eder.cid == CID_EDER_B_MMF:
            return True if self.regs.rx_drv_dco & 1 else False

    @lna_state.setter
    def lna_state(self, v):
        if v:
            self.regs.rx_drv_dco = set_bits(1)
        else:
            self.regs.rx_drv_dco = clear_bits(1)

    @property
    def bf_idx_reg(self):
        return self.regs.bf_rx_awv_ptr

    @bf_idx_reg.setter
    def bf_idx_reg(self, v):
        self.regs.bf_rx_awv_ptr = v
    
    @property
    def beamweights_reg(self):
        return self.regs.bf_rx_awv

    def measure_bb(self, l2samp=4):
        return measure_IQ(self.eder.adc, RX_IQ, l2samp)

    def measure_dco(self, l2samp=4):
        adc = self.eder.adc
        
        retval = measure_IQ(adc, RX_IQ, l2samp)

        retval.I.meas_dco(adc, adc.dco_i, adc.dco_i_dcsc, l2samp)
        retval.Q.meas_dco(adc, adc.dco_q, adc.dco_q_dcsc, l2samp)
        
        return retval

    
"""
    def dco_split(self, rx_drv_dco_reg):
        return {'sign':(rx_drv_dco_reg>>5)&0x1, 'offset':rx_drv_dco_reg&0x1f}
    
    def dco(self, sign, offset):
            return ((sign&0x1)<<5) + offset&0x1f


    def rx_drv_dco_cal(self, iq, mtype='sys'):
        if iq == 'i':
            diff = 'idiff'
        elif iq == 'q':
            diff = 'qdiff'
        else:
            print ('Invalid argument.')
            return

        sign = lambda x: x and (1, -1)[x < 0]

        selected_sign = -1

        START = 0
        MID = 1
        END = 2

        for offset_sign in range(0,2):
            self.set_drv_offset(iq, (offset_sign<<5))
            measured_values_0 = self.iq_meas.meas(meas_type=mtype)
            self.set_drv_offset(iq, (offset_sign<<5)|0x1f)
            measured_values_1 = self.iq_meas.meas(meas_type=mtype)
            if sign(measured_values_0[diff]) != sign(measured_values_1[diff]):
                selected_sign = offset_sign
                break

        if selected_sign == -1:
            self.logger.log_error('RX DRV DCO calibration failed!',2)
            return 0

        rx_drv_dco = [0,0,0]
        dco_diff = [0,0,0]

        rx_drv_dco[START] = 0
        rx_drv_dco[END] = 0x1F

        average = (rx_drv_dco[START] + rx_drv_dco[END]) / 2
        rx_drv_dco[MID] = int(round(average, 0))

        self.set_drv_offset(iq, (selected_sign<<5)|rx_drv_dco[START])
        measured_values = self.iq_meas.meas(meas_type=mtype)
        dco_diff[START] = measured_values[diff]

        self.set_drv_offset(iq, (selected_sign<<5)|rx_drv_dco[MID])
        measured_values = self.iq_meas.meas(meas_type=mtype)
        dco_diff[MID] = measured_values[diff]

        self.set_drv_offset(iq, (selected_sign<<5)|rx_drv_dco[END])
        measured_values = self.iq_meas.meas(meas_type=mtype)
        dco_diff[END] = measured_values[diff]

        while (abs(rx_drv_dco[START]-rx_drv_dco[MID]) > 1) or (abs(rx_drv_dco[MID]-rx_drv_dco[END]) > 1):
            if sign(dco_diff[START]) == sign(dco_diff[MID]):
                rx_drv_dco[START] = rx_drv_dco[MID]
                average = (rx_drv_dco[START] + rx_drv_dco[END]) / 2
                rx_drv_dco[MID] = int(round(average, 0))
                dco_diff[START] = dco_diff[MID]
                self.set_drv_offset(iq, (selected_sign<<5)|rx_drv_dco[MID])
                measured_values = self.iq_meas.meas(meas_type=mtype)
                dco_diff[MID] = measured_values[diff]
            elif sign(dco_diff[END]) == sign(dco_diff[MID]):
                rx_drv_dco[END] = rx_drv_dco[MID]
                average = (rx_drv_dco[START] + rx_drv_dco[END]) / 2
                rx_drv_dco[MID] = int(round(average, 0))
                dco_diff[END] = dco_diff[MID]
                self.set_drv_offset(iq, (selected_sign<<5)|rx_drv_dco[MID])
                measured_values = self.iq_meas.meas(meas_type=mtype)
                dco_diff[MID] = measured_values[diff]
            else:
                # mid_dco diff is 0'
                # Doubble check
                if dco_diff[MID] == 0:
                    self.set_drv_offset(iq, (selected_sign<<5)|rx_drv_dco[MID])
                    break
                else:
                    print (iq)
                    self.logger.log_info('Something went wrong!!!!',2)
                    return 0

        dco_diff = list(map(abs, dco_diff))
        i = dco_diff.index(min(dco_diff))
        self.set_drv_offset(iq, (selected_sign<<5)|rx_drv_dco[i])

        return (selected_sign<<5)|rx_drv_dco[i]

    def run(self, trx_ctrl=0x00, rx_dco_en=0x01, trx_rx_on=0x1E0000, trx_rx_off=0x1E0000, gain=((0,0),0x11,0x11,0x77), verbose=1):
        if verbose >= 0:
            self.logger.log_info('Rx DRV DCO calibration')
        if verbose >= 1:
            self.logger.log_info('Rx DRV DCO status before calibration start:')
            self.report()

        # Backup register values
        trx_ctrl_save   = self.regs.rd('trx_ctrl')
        rx_dco_en_save  = self.regs.rd('rx_dco_en')
        trx_rx_on_save  = self.regs.rd('trx_rx_on')
        trx_rx_off_save = self.regs.rd('trx_rx_off')
        bfrf_gain       = self.regs.rd('rx_gain_ctrl_bfrf')
        bb1_gain        = self.regs.rd('rx_gain_ctrl_bb1')
        bb2_gain        = self.regs.rd('rx_gain_ctrl_bb2')
        bb3_gain        = self.regs.rd('rx_gain_ctrl_bb3')
        rx_bb_i_dco     = self.regs.rd('rx_bb_i_dco')
        rx_bb_q_dco     = self.regs.rd('rx_bb_q_dco')
        
        # Modify control registers
        self.regs.wr('trx_ctrl',    trx_ctrl)
        self.regs.wr('trx_rx_on',   trx_rx_on)
        self.regs.wr('trx_rx_off',  trx_rx_off)
        self.regs.wr('rx_dco_en',   rx_dco_en)
        self.regs.wr('rx_bb_i_dco', 0x40)
        self.regs.wr('rx_bb_q_dco', 0x40)
        if verbose >= 1:
            self.logger.log_info('Change Control settings:')
            self.logger.log_info('trx_ctrl      : {:#04x}     => {:#04x}'.format(trx_ctrl_save,self.regs.rd('trx_ctrl')),2)
            self.logger.log_info('rx_dco_en     : {:#04x}     => {:#04x}'.format(rx_dco_en_save,self.regs.rd('rx_dco_en')),2)
            self.logger.log_info('trx_rx_on     : {:#08x} => {:#08x}'.format(trx_rx_on_save,self.regs.rd('trx_rx_on')),2)
            self.logger.log_info('trx_rx_off    : {:#08x} => {:#08x}'.format(trx_rx_off_save,self.regs.rd('trx_rx_off')),2)
            self.logger.log_info('rx_bb_i_dco   : {:#05x}    => {:#05x}'.format(rx_bb_i_dco,self.regs.rd('rx_bb_i_dco')),2)
            self.logger.log_info('rx_bb_q_dco   : {:#05x}    => {:#05x}'.format(rx_bb_q_dco,self.regs.rd('rx_bb_q_dco')),2)
            self.logger.log_info('Rx DRV DCO status after control register change:')
            self.report()

        # Modify gain registers
        if self.regs.device_info.get_attrib('chip_type') == 'Eder B MMF':
            lna_state = self.rx.lna_state()
            self.rx.lna_state(0)

        bfrf = bfrf_gain
        if gain[0][0] != None:
            bfrf = (bfrf & 0x0F) | (gain[0][0]<<4)
        if gain[0][1] != None:
            bfrf = (bfrf & 0xF0) | gain[0][1]
        self.regs.wr('rx_gain_ctrl_bfrf',bfrf)
        if gain[1] != None:
            self.regs.wr('rx_gain_ctrl_bb1', gain[1])
        if gain[2] != None:
            self.regs.wr('rx_gain_ctrl_bb2', gain[2])
        if gain[3] != None:
            self.regs.wr('rx_gain_ctrl_bb3', gain[3])
        if verbose >= 1:
            self.logger.log_info('Change Rx Gain settings:')
            self.logger.log_info('Rx BFRF gain  : {:#04x} => {:#04x}'.format(bfrf_gain,self.regs.rd('rx_gain_ctrl_bfrf')),2)
            self.logger.log_info('Rx BB1 gain   : {:#04x} => {:#04x}'.format(bb1_gain,self.regs.rd('rx_gain_ctrl_bb1')),2)
            self.logger.log_info('Rx BB2 gain   : {:#04x} => {:#04x}'.format(bb2_gain,self.regs.rd('rx_gain_ctrl_bb2')),2)
            self.logger.log_info('Rx BB3 gain   : {:#04x} => {:#04x}'.format(bb3_gain,self.regs.rd('rx_gain_ctrl_bb3')),2)
            if self.regs.device_info.get_attrib('chip_type') == 'Eder B MMF':
                self.logger.log_info('Rx LNA enable : {:#04x} => {:#04x}'.format(lna_state,self.rx.lna_state()),2)
            self.logger.log_info('Rx DRV DCO status after Rx gain change:')
            self.report(meas_type='sys')


        if verbose >= 0:
            self.logger.log_info('Rx DRV DCO status before calibration:')
            self.report()

        rx_drv_i_dco = self.rx_drv_dco_cal('i', 'sys')
        rx_drv_q_dco = self.rx_drv_dco_cal('q', 'sys')

        if verbose >= 0:
            self.logger.log_info('Rx DRV DCO status after calibration:')
            self.report()


        # Restore modified gain registers
        if verbose >= 1:
            self.logger.log_info('Restoring Rx Gain settings:')
            self.logger.log_info('Rx BFRF gain  : {:#04x} => {:#04x}'.format(self.regs.rd('rx_gain_ctrl_bfrf'),bfrf_gain),2)
            self.logger.log_info('Rx BB1 gain   : {:#04x} => {:#04x}'.format(self.regs.rd('rx_gain_ctrl_bb1'),bb1_gain),2)
            self.logger.log_info('Rx BB2 gain   : {:#04x} => {:#04x}'.format(self.regs.rd('rx_gain_ctrl_bb2'),bb2_gain),2)
            self.logger.log_info('Rx BB3 gain   : {:#04x} => {:#04x}'.format(self.regs.rd('rx_gain_ctrl_bb3'),bb3_gain),2)
            if self.regs.device_info.get_attrib('chip_type') == 'Eder B MMF':
                self.logger.log_info('Rx LNA enable : {:#04x} => {:#04x}'.format(self.rx.lna_state(),lna_state),2)
        if self.regs.device_info.get_attrib('chip_type') == 'Eder B MMF':
            self.rx.lna_state(lna_state)
        self.regs.wr('rx_gain_ctrl_bfrf', bfrf_gain)
        self.regs.wr('rx_gain_ctrl_bb1', bb1_gain)
        self.regs.wr('rx_gain_ctrl_bb2', bb2_gain)
        self.regs.wr('rx_gain_ctrl_bb3', bb3_gain)
        if verbose >= 2:
            self.logger.log_info('Rx DRV DCO status after Rx Gain restore:')
            self.report(meas_type='sys')

        # Restore modified control registers
        if verbose >= 1:
            self.logger.log_info('Restoring control settings:')
            self.logger.log_info('trx_ctrl      : {:#04x}     => {:#04x}'.format(self.regs.rd('trx_ctrl'),trx_ctrl_save),2)
            self.logger.log_info('rx_dco_en     : {:#04x}     => {:#04x}'.format(self.regs.rd('rx_dco_en'),rx_dco_en_save),2)
            self.logger.log_info('trx_rx_on     : {:#08x} => {:#08x}'.format(self.regs.rd('trx_rx_on'),trx_rx_on_save),2)
            self.logger.log_info('trx_rx_off    : {:#08x} => {:#08x}'.format(self.regs.rd('trx_rx_off'),trx_rx_off_save),2)
            self.logger.log_info('rx_bb_i_dco   : {:#05x}    => {:#05x}'.format(self.regs.rd('rx_bb_i_dco'),rx_bb_i_dco),2)
            self.logger.log_info('rx_bb_q_dco   : {:#05x}    => {:#05x}'.format(self.regs.rd('rx_bb_q_dco'),rx_bb_q_dco),2)
        self.regs.wr('trx_ctrl',    trx_ctrl_save)
        self.regs.wr('trx_rx_on',   trx_rx_on_save)
        self.regs.wr('trx_rx_off',  trx_rx_off_save)
        self.regs.wr('rx_dco_en',   rx_dco_en_save)
        self.regs.wr('rx_bb_i_dco', rx_bb_i_dco)
        self.regs.wr('rx_bb_q_dco', rx_bb_q_dco)
        
        if verbose >= 1:
            self.logger.log_info('Rx DRV DCO status after register restore:')
            self.report()

        if verbose >= 0:
            self.logger.log_info('Rx DRV DCO calibration done')
        return rx_drv_i_dco, rx_drv_q_dco



    # FOR TEST ONLY
    def sweep_drv_reg(self, iq='i'):
        trx_ctrl = self.regs.rd('trx_ctrl')
        if trx_ctrl & 0x1:
            self.regs.set('trx_rx_on', 0x040000)
        else:
            self.regs.set('trx_rx_off', 0x1f0000)
        self.regs.wr('rx_dco_en',0x01)
        if iq == 'q':
            self.regs.wr('rx_bb_q_dco', 0x40)
        else:
            self.regs.wr('rx_bb_i_dco', 0x40)
        for i in range(0,2):
            print ('**'+str(i))
            for j in range(0, 0x20):
                if iq == 'q':
                    self.set_drv_offset('q', (i<<5)|j)
                else:
                    self.set_drv_offset('i', (i<<5)|j)
                measured_values = self.iq_meas.meas(meas_type='sys')
                if iq == 'q':
                    print (hex(self.regs.rd('rx_drv_dco')) + ',' + hex((i<<5)|j) + ',' + str(measured_values['qdiff']))
                else:
                    print (hex(self.regs.rd('rx_drv_dco')) + ',' + hex((i<<5)|j) + ',' + str(measured_values['idiff']))

    # FOR TEST ONLY
    def sweep_drv_reg_0002(self, iq='i'):
        if iq == 'q':
            self.regs.wr('rx_bb_q_dco', 0x40)
        else:
            self.regs.wr('rx_bb_i_dco', 0x40)
        for i in range(0,2):
            print ('**'+str(i))
            for j in range(0, 0x20):
                if iq == 'q':
                    self.set_drv_offset('q', (i<<5)|j)
                else:
                    self.set_drv_offset('i', (i<<5)|j)
                measured_values = self.iq_meas.meas(meas_type='sys')
                if iq == 'q':
                    print (hex(self.regs.rd('rx_drv_dco')) + ',' + hex((i<<5)|j) + ',' + str(measured_values['qdiff']))
                else:
                    print (hex(self.regs.rd('rx_drv_dco')) + ',' + hex((i<<5)|j) + ',' + str(measured_values['idiff']))
"""
