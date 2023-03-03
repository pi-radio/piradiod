from piradio.devices.uio import UIO
from piradio.command import CommandObject, cmdproperty
from piradio.util import Freq, GHz, MHz

def reg(x):
    return x

class ADCBlock(CommandObject):
    EVENT_SOURCE_IMMEDIATE = 0

    UPDATE_EVENT_MASK = 0xF

    UPDATE_EVENT_SLICE = 0x1
    UPDATE_EVENT_NCO = 0x2
    UPDATE_EVENT_QMC = 0x4
    UPDATE_EVENT_COARSE_DELAY = 0x8 # differs for DAC
    
    NCO_UPDATE_MODE_MASK = 0x7

    NCO_DIV = 1 << 48
    
    def __init__(self, rfdc, tile, block):
        self.rfdc = rfdc
        self.tile = tile
        self.block = block

    @property
    def DRP(self):
        return self.rfdc.ADCRegs[self.tile].DRP[self.block]

    @property
    def sampling_rate(self):
        return GHz(self.rfdc.params.ADC[self.tile].sampling_rate)
    
    @cmdproperty
    def nco_freq(self):
        upp = self.DRP.NCO_FQWD_UPP
        mid = self.DRP.NCO_FQWD_MID
        low = self.DRP.NCO_FQWD_LOW

        v = ((upp << 32) | (mid << 16) | low) / self.NCO_DIV
        return self.sampling_rate * v

    @nco_freq.setter
    def nco_freq(self, f : Freq):
        assert f < self.sampling_rate
        assert f >= MHz(0.0)

        v = int(f * self.NCO_DIV / self.sampling_rate)

        self.DRP.NCO_FQWD_LOW = v & 0xFFFF
        self.DRP.NCO_FQWD_MID = (v >> 16) & 0xFFFF
        self.DRP.NCO_FQWD_UPP = (v >> 32) & 0xFFFF

        self.DRP.NCO_UPDT = (self.DRP.NCO_UPDT & ~self.NCO_UPDATE_MODE_MASK) | self.EVENT_SOURCE_IMMEDIATE
        self.DRP.ADC_UPDATE_DYN |= self.UPDATE_EVENT_NCO


class ADCTile:
    CLK_EN: reg(0x000)              # ADC Clock Enable Register
    ADC_DEBUG_RST: reg(0x004)       # ADC Debug Reset Register
    ADC_FABRIC_RATE: reg(0x008)     # ADC Fabric Rate Register
    ADC_FABRIC_RATE_OBS: reg(0x050) # ADC Obs Fabric Rate Register
    DAC_FABRIC_RATE: reg(0x008) # DAC Fabric Rate Register
    ADC_FABRIC: reg(0x00C) # ADC Fabric Register
    ADC_FABRIC_OBS: reg(0x054) # ADC Obs Fabric Register
    ADC_FABRIC_ISR: reg(0x010) # ADC Fabric ISR Register
    DAC_FIFO_START: reg(0x010) # DAC FIFO Start Register
    DAC_FABRIC_ISR: reg(0x014) # DAC Fabric ISR Register
    ADC_FABRIC_IMR: reg(0x014) # ADC Fabric IMR Register
    DAC_FABRIC_IMR: reg(0x018) # DAC Fabric IMR Register
    ADC_FABRIC_DBG: reg(0x018) # ADC Fabric Debug Register
    ADC_FABRIC_DBG_OBS: reg(0x058) # ADC Obs Fabric Debug Register
    ADC_UPDATE_DYN: reg(0x01C) # ADC Update Dynamic Register
    DAC_UPDATE_DYN: reg(0x020) # DAC Update Dynamic Register
    ADC_FIFO_LTNC_CRL: reg(0x020) # ADC FIFO Latency Control Register
    ADC_FIFO_LTNC_CRL_OBS: reg(0x064) # ADC Obs FIFO Latency Control Register
    ADC_DEC_ISR: reg(0x030) # ADC Decoder interface ISR Register
    DAC_DATAPATH: reg(0x034) # ADC Decoder interface IMR Register
    ADC_DEC_IMR: reg(0x034) # ADC Decoder interface IMR Register
    DATPATH_ISR: reg(0x038) # ADC Data Path ISR Register
    DATPATH_IMR: reg(0x03C) # ADC Data Path IMR Register
    ADC_DECI_CONFIG: reg(0x040) # ADC Decimation Config Register
    ADC_DECI_CONFIG_OBS: reg(0x048) # ADC Decimation Config Register
    DAC_INTERP_CTRL: reg(0x040) # DAC Interpolation Control Register
    ADC_DECI_MODE: reg(0x044) # ADC Decimation mode Register
    ADC_DECI_MODE_OBS: reg(0x04C) # ADC Obs Decimation mode Register
    DAC_ITERP_DATA: reg(0x044) # DAC interpolation data
    ADC_FABRIC_ISR_OBS: reg(0x05C) # ADC Fabric ISR Observation Register
    ADC_FABRIC_IMR_OBS: reg(0x060) # ADC Fabric ISR Observation Register
    DAC_TDD_MODE0: reg(0x060) # DAC TDD Mode 0 Configuration*/
    ADC_TDD_MODE0: reg(0x068) # ADC TDD Mode 0 Configuration*/
    ADC_MXR_CFG0: reg(0x080) # ADC I channel mixer config Register
    ADC_MXR_CFG1: reg(0x084) # ADC Q channel mixer config Register
    MXR_MODE: reg(0x088) # ADC/DAC mixer mode Register
    QMC_UPDT: reg(0x0C8) # ADC/DAC QMC Update Mode Register
    QMC_CFG: reg(0x0CC) # ADC/DAC QMC Config Register
    QMC_OFF: reg(0x0D0) # ADC/DAC QMC Offset Correction Register
    QMC_GAIN: reg(0x0D4) # ADC/DAC QMC Gain Correction Register
    QMC_PHASE: reg(0x0D8) # ADC/DAC QMC Phase Correction Register
    ADC_CRSE_DLY_UPDT: reg(0x0DC) # ADC Coarse Delay Update Register
    DAC_CRSE_DLY_UPDT: reg(0x0E0) # DAC Coarse Delay Update Register
    ADC_CRSE_DLY_CFG: reg(0x0E0) # ADC Coarse delay Config Register
    DAC_CRSE_DLY_CFG: reg(0x0DC) # DAC Coarse delay Config Register
    ADC_DAT_SCAL_CFG: reg(0x0E4) # ADC Data Scaling Config Register
    ADC_SWITCH_MATRX: reg(0x0E8) # ADC Switch Matrix Config Register
    ADC_TRSHD0_CFG: reg(0x0EC) # ADC Threshold0 Config Register
    ADC_TRSHD0_AVG_UP: reg(0x0F0) # ADC Threshold0 Average[31:16] Register
    ADC_TRSHD0_AVG_LO: reg(0x0F4) # ADC Threshold0 Average[15:0] Register
    ADC_TRSHD0_UNDER: reg(0x0F8) # ADC Threshold0 Under Threshold Register
    ADC_TRSHD0_OVER: reg(0x0FC) # ADC Threshold0 Over Threshold Register
    ADC_TRSHD1_CFG: reg(0x100) # ADC Threshold1 Config Register
    ADC_TRSHD1_AVG_UP: reg(0x104) # ADC Threshold1 Average[31:16] Register
    ADC_TRSHD1_AVG_LO: reg(0x108) # ADC Threshold1 Average[15:0] Register
    ADC_TRSHD1_UNDER: reg(0x10C) # ADC Threshold1 Under Threshold Register
    ADC_TRSHD1_OVER: reg(0x110) # ADC Threshold1 Over Threshold Register
    ADC_FEND_DAT_CRL: reg(0x140) # ADC Front end Data Control Register
    ADC_TI_DCB_CRL0: reg(0x144) # ADC Time Interleaved digital correction block gain control0 Register
    ADC_TI_DCB_CRL1: reg(0x148) # ADC Time Interleaved digital correction block gain control1 Register
    ADC_TI_DCB_CRL2: reg(0x14C) # ADC Time Interleaved digital correction block gain control2 Register
    ADC_TI_DCB_CRL3: reg(0x150) # ADC Time Interleaved digital correction block gain control3 Register
    ADC_TI_TISK_CRL0: reg(0x154) # ADC Time skew correction control bits0 Register
    DAC_MC_CFG0: reg(0x1C4) # Static Configuration  data for DAC Analog
    ADC_TI_TISK_CRL1: reg(0x158) # ADC Time skew correction control bits1 Register
    ADC_TI_TISK_CRL2: reg(0x15C) # ADC Time skew correction control bits2 Register
    ADC_TI_TISK_CRL3: reg(0x160) # ADC Time skew correction control bits3 Register
    ADC_TI_TISK_CRL4: reg(0x164) # ADC Time skew correction control bits4 Register
    ADC_TI_TISK_CRL5: reg(0x168) # ADC Time skew correction control bits5 Register (Gen 3 only)
    ADC_TI_TISK_DAC0: reg(0x168) # ADC Time skew DAC cal code of subadc ch0 Register(Below Gen 3)
    ADC_TI_TISK_DAC1: reg(0x16C) # ADC Time skew DAC cal code of subadc ch1 Register
    ADC_TI_TISK_DAC2: reg(0x170) # ADC Time skew DAC cal code of subadc ch2 Register
    ADC_TI_TISK_DAC3: reg(0x174) # ADC Time skew DAC cal code of subadc ch3 Register
    ADC_TI_TISK_DACP0: reg(0x178) # ADC Time skew DAC cal code of subadc ch0 Register
    ADC_TI_TISK_DACP1: reg(0x17C) # ADC Time skew DAC cal code of subadc ch1 Register
    ADC_TI_TISK_DACP2: reg(0x180) # ADC Time skew DAC cal code of subadc ch2 Register
    ADC_TI_TISK_DACP3: reg(0x184) # ADC Time skew DAC cal code of subadc ch3 Register
    DATA_SCALER: reg(0x190) # DAC Data Scaler Register
    DAC_VOP_CTRL: reg(0x198) # DAC variable output power control Register
    ADC0_SUBDRP_ADDR: reg(0x198) # subadc0, sub-drp address of target Register
    ADC0_SUBDRP_DAT: reg(0x19C) # subadc0, sub-drp data of target Register
    ADC1_SUBDRP_ADDR: reg(0x1A0) # subadc1, sub-drp address of target Register
    ADC1_SUBDRP_DAT: reg(0x1A4) # subadc1, sub-drp data of target Register
    ADC2_SUBDRP_ADDR: reg(0x1A8) # subadc2, sub-drp address of target Register
    ADC2_SUBDRP_DAT: reg(0x1AC) # subadc2, sub-drp data of target Register
    ADC3_SUBDRP_ADDR: reg(0x1B0) # subadc3, sub-drp address of target Register
    ADC3_SUBDRP_DAT: reg(0x1B4) # subadc3, sub-drp data of target Register
    ADC_RX_MC_PWRDWN: reg(0x1C0) # ADC Static configuration bits for ADC(RX) analog Register
    ADC_DAC_MC_CFG0: reg(0x1C4) # ADC/DAC Static configuration bits for ADC/DAC analog Register
    ADC_DAC_MC_CFG1: reg(0x1C8) # ADC/DAC Static configuration bits for ADC/DAC analog Register
    ADC_DAC_MC_CFG2: reg(0x1CC) # ADC/DAC Static configuration bits for ADC/DAC analog Register
    DAC_MC_CFG3: reg(0x1D0) # DAC Static configuration bits for DAC analog Register
    ADC_RXPR_MC_CFG0: reg(0x1D0) # ADC RX Pair static Configuration Register
    ADC_RXPR_MC_CFG1: reg(0x1D4) # ADC RX Pair static Configuration Register
    ADC_TI_DCBSTS0_BG: reg(0x200) # ADC DCB Status0 BG Register
    ADC_TI_DCBSTS0_FG: reg(0x204) # ADC DCB Status0 FG Register
    ADC_TI_DCBSTS1_BG: reg(0x208) # ADC DCB Status1 BG Register
    ADC_TI_DCBSTS1_FG: reg(0x20C) # ADC DCB Status1 FG Register
    ADC_TI_DCBSTS2_BG: reg(0x210) # ADC DCB Status2 BG Register
    ADC_TI_DCBSTS2_FG: reg(0x214) # ADC DCB Status2 FG Register
    ADC_TI_DCBSTS3_BG: reg(0x218) # ADC DCB Status3 BG Register
    ADC_TI_DCBSTS3_FG: reg(0x21C) # ADC DCB Status3 FG Register
    ADC_TI_DCBSTS4_MB: reg(0x220) # ADC DCB Status4 MSB Register
    ADC_TI_DCBSTS4_LB: reg(0x224) # ADC DCB Status4 LSB Register
    ADC_TI_DCBSTS5_MB: reg(0x228) # ADC DCB Status5 MSB Register
    ADC_TI_DCBSTS5_LB: reg(0x22C) # ADC DCB Status5 LSB Register
    ADC_TI_DCBSTS6_MB: reg(0x230) # ADC DCB Status6 MSB Register
    ADC_TI_DCBSTS6_LB: reg(0x234) # ADC DCB Status6 LSB Register
    ADC_TI_DCBSTS7_MB: reg(0x238) # ADC DCB Status7 MSB Register
    ADC_TI_DCBSTS7_LB: reg(0x23C) # ADC DCB Status7 LSB Register
    DSA_UPDT: reg(0x254) # ADC DSA Update Trigger REgister
    ADC_FIFO_LTNCY_LB: reg(0x280) # ADC FIFO Latency measurement LSB Register
    ADC_FIFO_LTNCY_MB: reg(0x284) # ADC FIFO Latency measurement MSB Register
    DAC_DECODER_CTRL: reg(0x180) # DAC Unary Decoder/ Randomizer settings
    DAC_DECODER_CLK: reg(0x184) # Decoder Clock enable
    MB_CONFIG: reg(0x308) # Multiband Config status

    ADC_SIG_DETECT_CTRL: reg(0x114) # ADC Signal Detector Control
    ADC_SIG_DETECT_THRESHOLD0_LEVEL: reg(0x118) # ADC Signal Detector Threshold 0
    ADC_SIG_DETECT_THRESHOLD0_CNT_OFF: reg(0x11C) # ADC Signal Detector Threshold 0 on Counter
    ADC_SIG_DETECT_THRESHOLD0_CNT_ON: reg(0x120) # ADC Signal Detector Threshold 0 off Counter
    ADC_SIG_DETECT_MAGN: reg(0x130) # ADC Signal Detector Magintude

    HSCOM_CLK_DSTR: reg(0x088) # Clock Distribution Register*/
    HSCOM_CLK_DSTR_MASK: reg(0xC788) # Clock Distribution Register*/
    HSCOM_CLK_DSTR_MASK_ALT: reg(0x1870) # Clock Distribution Register for Intratile*/
    HSCOM_PWR: reg(0x094) # Control register during power-up sequence
    HSCOM_CLK_DIV: reg(0xB0) # Fabric clk out divider
    HSCOM_PWR_STATE: reg(0xB4) # Check powerup state
    HSCOM_UPDT_DYN: reg(0x0B8) # Trigger the update dynamic event
    HSCOM_EFUSE_2: reg(0x144)
    DAC_INVSINC: reg(0x0C0) # Invsinc control
    DAC_MB_CFG: reg(0x0C4) # Multiband config
    MTS_SRDIST: reg(0x1CA0)
    #MTS_SRCAP_T1  (0x24 << 2)
    #MTS_SRCAP_PLL (0x0C << 2)
    #MTS_SRCAP_DIG (0x2C << 2)
    #MTS_SRDTC_T1 (0x27U << 2)
    #MTS_SRDTC_PLL (0x26U << 2)
    #MTS_SRFLAG (0x49U << 2)
    #MTS_CLKSTAT (0x24U << 2)
    MTS_SRCOUNT_CTRL: reg(0x004C)
    MTS_SRCOUNT_VAL: reg(0x0050)
    MTS_SRFREQ_VAL: reg(0x0054)
    MTS_FIFO_CTRL_ADC: reg(0x0010)
    MTS_FIFO_CTRL_DAC: reg(0x0014)
    MTS_DELAY_CTRL: reg(0x0028)
    MTS_ADC_MARKER: reg(0x0018)
    #MTS_ADC_MARKER_CNT: reg(0x0010U
    #MTS_DAC_MARKER_CTRL: reg(0x0048U
    #MTS_DAC_MARKER_CNT (0x92U << 2)
    #MTS_DAC_MARKER_LOC (0x93U << 2)
    #MTS_DAC_FIFO_MARKER_CTRL (0x94U << 2)
    #MTS_DAC_FABRIC: reg(0x0C

    RESET: reg(0x00) # Tile reset register
    RESTART: reg(0x04) # Tile restart register
    RESTART_STATE: reg(0x08) # Tile restart state register
    CURRENT_STATE: reg(0x0C) # Current state register
    CLOCK_DETECT: reg(0x80) # Clock detect register
    STATUS: reg(0x228) # Common status register
    CAL_DIV_BYP: reg(0x100) # Calibration divider bypass register
    COMMON_INTR_STS: reg(0x100) # Common Intr Status register
    COMMON_INTR_ENABLE: reg(0x104) # Common Intr enable register
    INTR_STS: reg(0x200) # Intr status register
    INTR_ENABLE: reg(0x204) # Intr enable register
    #CONV_INTR_STS(X) (0x208U + (X *: reg(0x08))
    #CONV_INTR_EN(X) (0x20CU + (X *: reg(0x08))
    #CONV_CAL_STGS(X) (0x234U + (X *: reg(0x04))
    #CONV_DSA_STGS(X) (0x244U + (X *: reg(0x04))
    #CAL_GCB_COEFF0_FAB(X) (0x280U + (X *: reg(0x10))
    #CAL_GCB_COEFF1_FAB(X) (0x284U + (X *: reg(0x10))
    #CAL_GCB_COEFF2_FAB(X) (0x288U + (X *: reg(0x10))
    #CAL_GCB_COEFF3_FAB(X) (0x28CU + (X *: reg(0x10))
    #TDD_CTRL_SLICE(X) (0x260 + (X *: reg(0x04))) # TDD control registers
    PLL_FREQ: reg(0x300) # PLL output frequency (before divider) register
    PLL_FS: reg(0x304) # Sampling rate register
    CAL_TMR_MULT: reg(0x30C) # Calibration timer register
    CAL_DLY: reg(0x310) # Calibration delay register
    CPL_TYPE: reg(0x314) # Coupling type register
    FIFO_ENABLE: reg(0x230) # FIFO Enable and Disable
    PLL_SDM_CFG0: reg(0x00) # PLL Configuration bits for sdm
    PLL_SDM_SEED0: reg(0x18) # PLL Bits for sdm LSB
    PLL_SDM_SEED1: reg(0x1C) # PLL Bits for sdm MSB
    PLL_VREG: reg(0x44) # PLL bits for voltage regulator
    PLL_VCO0: reg(0x54) # PLL bits for coltage controlled oscillator LSB
    PLL_VCO1: reg(0x58) # PLL bits for coltage controlled oscillator MSB
    PLL_CRS1: reg(0x28) # PLL bits for coarse frequency control LSB
    PLL_CRS2: reg(0x2C) # PLL bits for coarse frequency control MSB
    PLL_DIVIDER0: reg(0x30) # PLL Output Divider LSB register
    PLL_DIVIDER1: reg(0x34) # PLL Output Divider MSB register
    PLL_SPARE0: reg(0x38) # PLL spare inputs LSB
    PLL_SPARE1: reg(0x3C) # PLL spare inputs MSB
    PLL_REFDIV: reg(0x40) # PLL Reference Divider register
    PLL_VREG: reg(0x44) # PLL voltage regulator
    PLL_CHARGEPUMP: reg(0x48) # PLL bits for charge pumps
    PLL_LPF0: reg(0x4C) # PLL bits for loop filters LSB
    PLL_LPF1: reg(0x50) # PLL bits for loop filters MSB
    PLL_FPDIV: reg(0x5C) # PLL Feedback Divider register
    CLK_NETWORK_CTRL0: reg(0x8C) # Clock network control and trim register
    CLK_NETWORK_CTRL1: reg(0x90) # Multi-tile sync and clock source control register

    """
    #ADC_FABRIC_RATE_TDD(X)                                                                            \
	((X == 0) ? ADC_FABRIC_RATE :                                                                     \
		    ADC_FABRIC_RATE_OBS)) # ADC Fabric Rate (or OBS) Register TDD Selected
    ADC_FABRIC_TDD(X)                                                                                 \
	((X == 0) ? ADC_FABRIC :                                                                          \
		    ADC_FABRIC_OBS)) # ADC Fabric Register (or OBS) TDD Selected*/
    ADC_FABRIC_DBG_TDD(X)                                                                             \
	((X == 0) ? ADC_FABRIC_DBG :                                                                      \
		    ADC_FABRIC_DBG_OBS)) # ADC Fabric Debug (or OBS) Register TDD Selected
    ADC_FIFO_LTNC_CRL_TDD(X)                                                                          \
	((X == 0) ?                                                                                                    \
		 ADC_FIFO_LTNC_CRL :                                                                      \
		 ADC_FIFO_LTNC_CRL_OBS)) # ADC FIFO Latency Control (or OBS) Register TDD Selected
    ADC_DECI_CONFIG_TDD(X)                                                                            \
	((X == 0) ? ADC_DECI_CONFIG :                                                                     \
		    ADC_DECI_CONFIG_OBS)) # ADC Decimation Config (or OBS) Register TDD Selected
    ADC_DECI_MODE_TDD(X)                                                                              \
	((X == 0) ? ADC_DECI_MODE :                                                                       \
		    ADC_DECI_MODE_OBS)) # ADC Decimation mode (or OBS) Register TDD Selected
    TDD_MODE0(X)                                                                                      \
	((X == 0) ? ADC_TDD_MODE0 : DAC_TDD_MODE0)) # ADC TDD Mode 0 Configuration*/
    """

