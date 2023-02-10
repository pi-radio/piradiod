from piradio.devices.uio import UIO, UIOWindow, UIORegister

class ADCTile(UIOWindow):
    XRFDC_CLK_EN_OFFSET = UIORegister(0x000)              # ADC Clock Enable Register
    XRFDC_ADC_DEBUG_RST_OFFSET = UIORegister(0x004)       # ADC Debug Reset Register
    XRFDC_ADC_FABRIC_RATE_OFFSET = UIORegister(0x008)     # ADC Fabric Rate Register
    XRFDC_ADC_FABRIC_RATE_OBS_OFFSET = UIORegister(0x050) # ADC Obs Fabric Rate Register
    XRFDC_DAC_FABRIC_RATE_OFFSET = UIORegister(0x008) # DAC Fabric Rate Register
    XRFDC_ADC_FABRIC_OFFSET = UIORegister(0x00C) # ADC Fabric Register
    XRFDC_ADC_FABRIC_OBS_OFFSET = UIORegister(0x054) # ADC Obs Fabric Register
    XRFDC_ADC_FABRIC_ISR_OFFSET = UIORegister(0x010) # ADC Fabric ISR Register
    XRFDC_DAC_FIFO_START_OFFSET = UIORegister(0x010) # DAC FIFO Start Register
    XRFDC_DAC_FABRIC_ISR_OFFSET = UIORegister(0x014) # DAC Fabric ISR Register
    XRFDC_ADC_FABRIC_IMR_OFFSET = UIORegister(0x014) # ADC Fabric IMR Register
    XRFDC_DAC_FABRIC_IMR_OFFSET = UIORegister(0x018) # DAC Fabric IMR Register
    XRFDC_ADC_FABRIC_DBG_OFFSET = UIORegister(0x018) # ADC Fabric Debug Register
    XRFDC_ADC_FABRIC_DBG_OBS_OFFSET = UIORegister(0x058) # ADC Obs Fabric Debug Register
    XRFDC_ADC_UPDATE_DYN_OFFSET = UIORegister(0x01C) # ADC Update Dynamic Register
    XRFDC_DAC_UPDATE_DYN_OFFSET = UIORegister(0x020) # DAC Update Dynamic Register
    XRFDC_ADC_FIFO_LTNC_CRL_OFFSET = UIORegister(0x020) # ADC FIFO Latency Control Register
    XRFDC_ADC_FIFO_LTNC_CRL_OBS_OFFSET = UIORegister(0x064) # ADC Obs FIFO Latency Control Register
    XRFDC_ADC_DEC_ISR_OFFSET = UIORegister(0x030) # ADC Decoder interface ISR Register
    XRFDC_DAC_DATAPATH_OFFSET = UIORegister(0x034) # ADC Decoder interface IMR Register
    XRFDC_ADC_DEC_IMR_OFFSET = UIORegister(0x034) # ADC Decoder interface IMR Register
    XRFDC_DATPATH_ISR_OFFSET = UIORegister(0x038) # ADC Data Path ISR Register
    XRFDC_DATPATH_IMR_OFFSET = UIORegister(0x03C) # ADC Data Path IMR Register
    XRFDC_ADC_DECI_CONFIG_OFFSET = UIORegister(0x040) # ADC Decimation Config Register
    XRFDC_ADC_DECI_CONFIG_OBS_OFFSET = UIORegister(0x048) # ADC Decimation Config Register
    XRFDC_DAC_INTERP_CTRL_OFFSET = UIORegister(0x040) # DAC Interpolation Control Register
    XRFDC_ADC_DECI_MODE_OFFSET = UIORegister(0x044) # ADC Decimation mode Register
    XRFDC_ADC_DECI_MODE_OBS_OFFSET = UIORegister(0x04C) # ADC Obs Decimation mode Register
    XRFDC_DAC_ITERP_DATA_OFFSET = UIORegister(0x044) # DAC interpolation data
    XRFDC_ADC_FABRIC_ISR_OBS_OFFSET = UIORegister(0x05C) # ADC Fabric ISR Observation Register
    XRFDC_ADC_FABRIC_IMR_OBS_OFFSET = UIORegister(0x060) # ADC Fabric ISR Observation Register
    XRFDC_DAC_TDD_MODE0_OFFSET = UIORegister(0x060) # DAC TDD Mode 0 Configuration*/
    XRFDC_ADC_TDD_MODE0_OFFSET = UIORegister(0x068) # ADC TDD Mode 0 Configuration*/
    XRFDC_ADC_MXR_CFG0_OFFSET = UIORegister(0x080) # ADC I channel mixer config Register
    XRFDC_ADC_MXR_CFG1_OFFSET = UIORegister(0x084) # ADC Q channel mixer config Register
    XRFDC_MXR_MODE_OFFSET = UIORegister(0x088) # ADC/DAC mixer mode Register
    XRFDC_NCO_UPDT_OFFSET = UIORegister(0x08C) # ADC/DAC NCO Update mode Register
    XRFDC_NCO_RST_OFFSET = UIORegister(0x090) # ADC/DAC NCO Phase Reset Register
    XRFDC_ADC_NCO_FQWD_UPP_OFFSET = UIORegister(0x094) # ADC NCO Frequency Word[47:32] Register
    XRFDC_ADC_NCO_FQWD_MID_OFFSET = UIORegister(0x098) # ADC NCO Frequency Word[31:16] Register
    XRFDC_ADC_NCO_FQWD_LOW_OFFSET = UIORegister(0x09C) # ADC NCO Frequency Word[15:0] Register
    XRFDC_NCO_PHASE_UPP_OFFSET = UIORegister(0x0A0) # ADC/DAC NCO Phase[17:16] Register
    XRFDC_NCO_PHASE_LOW_OFFSET = UIORegister(0x0A4) # ADC/DAC NCO Phase[15:0] Register
    XRFDC_ADC_NCO_PHASE_MOD_OFFSET = UIORegister(0x0A8) # ADC NCO Phase Mode Register
    XRFDC_QMC_UPDT_OFFSET = UIORegister(0x0C8) # ADC/DAC QMC Update Mode Register
    XRFDC_QMC_CFG_OFFSET = UIORegister(0x0CC) # ADC/DAC QMC Config Register
    XRFDC_QMC_OFF_OFFSET = UIORegister(0x0D0) # ADC/DAC QMC Offset Correction Register
    XRFDC_QMC_GAIN_OFFSET = UIORegister(0x0D4) # ADC/DAC QMC Gain Correction Register
    XRFDC_QMC_PHASE_OFFSET = UIORegister(0x0D8) # ADC/DAC QMC Phase Correction Register
    XRFDC_ADC_CRSE_DLY_UPDT_OFFSET = UIORegister(0x0DC) # ADC Coarse Delay Update Register
    XRFDC_DAC_CRSE_DLY_UPDT_OFFSET = UIORegister(0x0E0) # DAC Coarse Delay Update Register
    XRFDC_ADC_CRSE_DLY_CFG_OFFSET = UIORegister(0x0E0) # ADC Coarse delay Config Register
    XRFDC_DAC_CRSE_DLY_CFG_OFFSET = UIORegister(0x0DC) # DAC Coarse delay Config Register
    XRFDC_ADC_DAT_SCAL_CFG_OFFSET = UIORegister(0x0E4) # ADC Data Scaling Config Register
    XRFDC_ADC_SWITCH_MATRX_OFFSET = UIORegister(0x0E8) # ADC Switch Matrix Config Register
    XRFDC_ADC_TRSHD0_CFG_OFFSET = UIORegister(0x0EC) # ADC Threshold0 Config Register
    XRFDC_ADC_TRSHD0_AVG_UP_OFFSET = UIORegister(0x0F0) # ADC Threshold0 Average[31:16] Register
    XRFDC_ADC_TRSHD0_AVG_LO_OFFSET = UIORegister(0x0F4) # ADC Threshold0 Average[15:0] Register
    XRFDC_ADC_TRSHD0_UNDER_OFFSET = UIORegister(0x0F8) # ADC Threshold0 Under Threshold Register
    XRFDC_ADC_TRSHD0_OVER_OFFSET = UIORegister(0x0FC) # ADC Threshold0 Over Threshold Register
    XRFDC_ADC_TRSHD1_CFG_OFFSET = UIORegister(0x100) # ADC Threshold1 Config Register
    XRFDC_ADC_TRSHD1_AVG_UP_OFFSET = UIORegister(0x104) # ADC Threshold1 Average[31:16] Register
    XRFDC_ADC_TRSHD1_AVG_LO_OFFSET = UIORegister(0x108) # ADC Threshold1 Average[15:0] Register
    XRFDC_ADC_TRSHD1_UNDER_OFFSET = UIORegister(0x10C) # ADC Threshold1 Under Threshold Register
    XRFDC_ADC_TRSHD1_OVER_OFFSET = UIORegister(0x110) # ADC Threshold1 Over Threshold Register
    XRFDC_ADC_FEND_DAT_CRL_OFFSET = UIORegister(0x140) # ADC Front end Data Control Register
    XRFDC_ADC_TI_DCB_CRL0_OFFSET = UIORegister(0x144) # ADC Time Interleaved digital correction block gain control0 Register
    XRFDC_ADC_TI_DCB_CRL1_OFFSET = UIORegister(0x148) # ADC Time Interleaved digital correction block gain control1 Register
    XRFDC_ADC_TI_DCB_CRL2_OFFSET = UIORegister(0x14C) # ADC Time Interleaved digital correction block gain control2 Register
    XRFDC_ADC_TI_DCB_CRL3_OFFSET = UIORegister(0x150) # ADC Time Interleaved digital correction block gain control3 Register
    XRFDC_ADC_TI_TISK_CRL0_OFFSET = UIORegister(0x154) # ADC Time skew correction control bits0 Register
    XRFDC_DAC_MC_CFG0_OFFSET = UIORegister(0x1C4) # Static Configuration  data for DAC Analog
    XRFDC_ADC_TI_TISK_CRL1_OFFSET = UIORegister(0x158) # ADC Time skew correction control bits1 Register
    XRFDC_ADC_TI_TISK_CRL2_OFFSET = UIORegister(0x15C) # ADC Time skew correction control bits2 Register
    XRFDC_ADC_TI_TISK_CRL3_OFFSET = UIORegister(0x160) # ADC Time skew correction control bits3 Register
    XRFDC_ADC_TI_TISK_CRL4_OFFSET = UIORegister(0x164) # ADC Time skew correction control bits4 Register
    XRFDC_ADC_TI_TISK_CRL5_OFFSET = UIORegister(0x168) # ADC Time skew correction control bits5 Register (Gen 3 only)
    XRFDC_ADC_TI_TISK_DAC0_OFFSET = UIORegister(0x168) # ADC Time skew DAC cal code of subadc ch0 Register(Below Gen 3)
    XRFDC_ADC_TI_TISK_DAC1_OFFSET = UIORegister(0x16C) # ADC Time skew DAC cal code of subadc ch1 Register
    XRFDC_ADC_TI_TISK_DAC2_OFFSET = UIORegister(0x170) # ADC Time skew DAC cal code of subadc ch2 Register
    XRFDC_ADC_TI_TISK_DAC3_OFFSET = UIORegister(0x174) # ADC Time skew DAC cal code of subadc ch3 Register
    XRFDC_ADC_TI_TISK_DACP0_OFFSET = UIORegister(0x178) # ADC Time skew DAC cal code of subadc ch0 Register
    XRFDC_ADC_TI_TISK_DACP1_OFFSET = UIORegister(0x17C) # ADC Time skew DAC cal code of subadc ch1 Register
    XRFDC_ADC_TI_TISK_DACP2_OFFSET = UIORegister(0x180) # ADC Time skew DAC cal code of subadc ch2 Register
    XRFDC_ADC_TI_TISK_DACP3_OFFSET = UIORegister(0x184) # ADC Time skew DAC cal code of subadc ch3 Register
    XRFDC_DATA_SCALER_OFFSET = UIORegister(0x190) # DAC Data Scaler Register
    XRFDC_DAC_VOP_CTRL_OFFSET = UIORegister(0x198) # DAC variable output power control Register
    XRFDC_ADC0_SUBDRP_ADDR_OFFSET = UIORegister(0x198) # subadc0, sub-drp address of target Register
    XRFDC_ADC0_SUBDRP_DAT_OFFSET = UIORegister(0x19C) # subadc0, sub-drp data of target Register
    XRFDC_ADC1_SUBDRP_ADDR_OFFSET = UIORegister(0x1A0) # subadc1, sub-drp address of target Register
    XRFDC_ADC1_SUBDRP_DAT_OFFSET = UIORegister(0x1A4) # subadc1, sub-drp data of target Register
    XRFDC_ADC2_SUBDRP_ADDR_OFFSET = UIORegister(0x1A8) # subadc2, sub-drp address of target Register
    XRFDC_ADC2_SUBDRP_DAT_OFFSET = UIORegister(0x1AC) # subadc2, sub-drp data of target Register
    XRFDC_ADC3_SUBDRP_ADDR_OFFSET = UIORegister(0x1B0) # subadc3, sub-drp address of target Register
    XRFDC_ADC3_SUBDRP_DAT_OFFSET = UIORegister(0x1B4) # subadc3, sub-drp data of target Register
    XRFDC_ADC_RX_MC_PWRDWN_OFFSET = UIORegister(0x1C0) # ADC Static configuration bits for ADC(RX) analog Register
    XRFDC_ADC_DAC_MC_CFG0_OFFSET = UIORegister(0x1C4) # ADC/DAC Static configuration bits for ADC/DAC analog Register
    XRFDC_ADC_DAC_MC_CFG1_OFFSET = UIORegister(0x1C8) # ADC/DAC Static configuration bits for ADC/DAC analog Register
    XRFDC_ADC_DAC_MC_CFG2_OFFSET = UIORegister(0x1CC) # ADC/DAC Static configuration bits for ADC/DAC analog Register
    XRFDC_DAC_MC_CFG3_OFFSET = UIORegister(0x1D0) # DAC Static configuration bits for DAC analog Register
    XRFDC_ADC_RXPR_MC_CFG0_OFFSET = UIORegister(0x1D0) # ADC RX Pair static Configuration Register
    XRFDC_ADC_RXPR_MC_CFG1_OFFSET = UIORegister(0x1D4) # ADC RX Pair static Configuration Register
    XRFDC_ADC_TI_DCBSTS0_BG_OFFSET = UIORegister(0x200) # ADC DCB Status0 BG Register
    XRFDC_ADC_TI_DCBSTS0_FG_OFFSET = UIORegister(0x204) # ADC DCB Status0 FG Register
    XRFDC_ADC_TI_DCBSTS1_BG_OFFSET = UIORegister(0x208) # ADC DCB Status1 BG Register
    XRFDC_ADC_TI_DCBSTS1_FG_OFFSET = UIORegister(0x20C) # ADC DCB Status1 FG Register
    XRFDC_ADC_TI_DCBSTS2_BG_OFFSET = UIORegister(0x210) # ADC DCB Status2 BG Register
    XRFDC_ADC_TI_DCBSTS2_FG_OFFSET = UIORegister(0x214) # ADC DCB Status2 FG Register
    XRFDC_ADC_TI_DCBSTS3_BG_OFFSET = UIORegister(0x218) # ADC DCB Status3 BG Register
    XRFDC_ADC_TI_DCBSTS3_FG_OFFSET = UIORegister(0x21C) # ADC DCB Status3 FG Register
    XRFDC_ADC_TI_DCBSTS4_MB_OFFSET = UIORegister(0x220) # ADC DCB Status4 MSB Register
    XRFDC_ADC_TI_DCBSTS4_LB_OFFSET = UIORegister(0x224) # ADC DCB Status4 LSB Register
    XRFDC_ADC_TI_DCBSTS5_MB_OFFSET = UIORegister(0x228) # ADC DCB Status5 MSB Register
    XRFDC_ADC_TI_DCBSTS5_LB_OFFSET = UIORegister(0x22C) # ADC DCB Status5 LSB Register
    XRFDC_ADC_TI_DCBSTS6_MB_OFFSET = UIORegister(0x230) # ADC DCB Status6 MSB Register
    XRFDC_ADC_TI_DCBSTS6_LB_OFFSET = UIORegister(0x234) # ADC DCB Status6 LSB Register
    XRFDC_ADC_TI_DCBSTS7_MB_OFFSET = UIORegister(0x238) # ADC DCB Status7 MSB Register
    XRFDC_ADC_TI_DCBSTS7_LB_OFFSET = UIORegister(0x23C) # ADC DCB Status7 LSB Register
    XRFDC_DSA_UPDT_OFFSET = UIORegister(0x254) # ADC DSA Update Trigger REgister
    XRFDC_ADC_FIFO_LTNCY_LB_OFFSET = UIORegister(0x280) # ADC FIFO Latency measurement LSB Register
    XRFDC_ADC_FIFO_LTNCY_MB_OFFSET = UIORegister(0x284) # ADC FIFO Latency measurement MSB Register
    XRFDC_DAC_DECODER_CTRL_OFFSET = UIORegister(0x180) # DAC Unary Decoder/ Randomizer settings
    XRFDC_DAC_DECODER_CLK_OFFSET = UIORegister(0x184) # Decoder Clock enable
    XRFDC_MB_CONFIG_OFFSET = UIORegister(0x308) # Multiband Config status

    XRFDC_ADC_SIG_DETECT_CTRL_OFFSET = UIORegister(0x114) # ADC Signal Detector Control
    XRFDC_ADC_SIG_DETECT_THRESHOLD0_LEVEL_OFFSET = UIORegister(0x118) # ADC Signal Detector Threshold 0
    XRFDC_ADC_SIG_DETECT_THRESHOLD0_CNT_OFF_OFFSET = UIORegister(0x11C) # ADC Signal Detector Threshold 0 on Counter
    XRFDC_ADC_SIG_DETECT_THRESHOLD0_CNT_ON_OFFSET = UIORegister(0x120) # ADC Signal Detector Threshold 0 off Counter
    XRFDC_ADC_SIG_DETECT_MAGN_OFFSET = UIORegister(0x130) # ADC Signal Detector Magintude

    XRFDC_HSCOM_CLK_DSTR_OFFSET = UIORegister(0x088) # Clock Distribution Register*/
    XRFDC_HSCOM_CLK_DSTR_MASK = UIORegister(0xC788) # Clock Distribution Register*/
    XRFDC_HSCOM_CLK_DSTR_MASK_ALT = UIORegister(0x1870) # Clock Distribution Register for Intratile*/
    XRFDC_HSCOM_PWR_OFFSET = UIORegister(0x094) # Control register during power-up sequence
    XRFDC_HSCOM_CLK_DIV_OFFSET = UIORegister(0xB0) # Fabric clk out divider
    XRFDC_HSCOM_PWR_STATE_OFFSET = UIORegister(0xB4) # Check powerup state
    XRFDC_HSCOM_UPDT_DYN_OFFSET = UIORegister(0x0B8) # Trigger the update dynamic event
    XRFDC_HSCOM_EFUSE_2_OFFSET = UIORegister(0x144)
    XRFDC_DAC_INVSINC_OFFSET = UIORegister(0x0C0) # Invsinc control
    XRFDC_DAC_MB_CFG_OFFSET = UIORegister(0x0C4) # Multiband config
    XRFDC_MTS_SRDIST = UIORegister(0x1CA0)
    #XRFDC_MTS_SRCAP_T1  (0x24 << 2)
    #XRFDC_MTS_SRCAP_PLL (0x0C << 2)
    #XRFDC_MTS_SRCAP_DIG (0x2C << 2)
    #XRFDC_MTS_SRDTC_T1 (0x27U << 2)
    #XRFDC_MTS_SRDTC_PLL (0x26U << 2)
    #XRFDC_MTS_SRFLAG (0x49U << 2)
    #XRFDC_MTS_CLKSTAT (0x24U << 2)
    XRFDC_MTS_SRCOUNT_CTRL = UIORegister(0x004C)
    XRFDC_MTS_SRCOUNT_VAL = UIORegister(0x0050)
    XRFDC_MTS_SRFREQ_VAL = UIORegister(0x0054)
    XRFDC_MTS_FIFO_CTRL_ADC = UIORegister(0x0010)
    XRFDC_MTS_FIFO_CTRL_DAC = UIORegister(0x0014)
    XRFDC_MTS_DELAY_CTRL = UIORegister(0x0028)
    XRFDC_MTS_ADC_MARKER = UIORegister(0x0018)
    #XRFDC_MTS_ADC_MARKER_CNT = UIORegister(0x0010U
    #XRFDC_MTS_DAC_MARKER_CTRL = UIORegister(0x0048U
    #XRFDC_MTS_DAC_MARKER_CNT (0x92U << 2)
    #XRFDC_MTS_DAC_MARKER_LOC (0x93U << 2)
    #XRFDC_MTS_DAC_FIFO_MARKER_CTRL (0x94U << 2)
    #XRFDC_MTS_DAC_FABRIC_OFFSET = UIORegister(0x0C

    XRFDC_RESET_OFFSET = UIORegister(0x00) # Tile reset register
    XRFDC_RESTART_OFFSET = UIORegister(0x04) # Tile restart register
    XRFDC_RESTART_STATE_OFFSET = UIORegister(0x08) # Tile restart state register
    XRFDC_CURRENT_STATE_OFFSET = UIORegister(0x0C) # Current state register
    XRFDC_CLOCK_DETECT_OFFSET = UIORegister(0x80) # Clock detect register
    XRFDC_STATUS_OFFSET = UIORegister(0x228) # Common status register
    XRFDC_CAL_DIV_BYP_OFFSET = UIORegister(0x100) # Calibration divider bypass register
    XRFDC_COMMON_INTR_STS = UIORegister(0x100) # Common Intr Status register
    XRFDC_COMMON_INTR_ENABLE = UIORegister(0x104) # Common Intr enable register
    XRFDC_INTR_STS = UIORegister(0x200) # Intr status register
    XRFDC_INTR_ENABLE = UIORegister(0x204) # Intr enable register
    #XRFDC_CONV_INTR_STS(X) (0x208U + (X * = UIORegister(0x08))
    #XRFDC_CONV_INTR_EN(X) (0x20CU + (X * = UIORegister(0x08))
    #XRFDC_CONV_CAL_STGS(X) (0x234U + (X * = UIORegister(0x04))
    #XRFDC_CONV_DSA_STGS(X) (0x244U + (X * = UIORegister(0x04))
    #XRFDC_CAL_GCB_COEFF0_FAB(X) (0x280U + (X * = UIORegister(0x10))
    #XRFDC_CAL_GCB_COEFF1_FAB(X) (0x284U + (X * = UIORegister(0x10))
    #XRFDC_CAL_GCB_COEFF2_FAB(X) (0x288U + (X * = UIORegister(0x10))
    #XRFDC_CAL_GCB_COEFF3_FAB(X) (0x28CU + (X * = UIORegister(0x10))
    #XRFDC_TDD_CTRL_SLICE_OFFSET(X) (0x260 + (X * = UIORegister(0x04))) # TDD control registers
    XRFDC_PLL_FREQ = UIORegister(0x300) # PLL output frequency (before divider) register
    XRFDC_PLL_FS = UIORegister(0x304) # Sampling rate register
    XRFDC_CAL_TMR_MULT_OFFSET = UIORegister(0x30C) # Calibration timer register
    XRFDC_CAL_DLY_OFFSET = UIORegister(0x310) # Calibration delay register
    XRFDC_CPL_TYPE_OFFSET = UIORegister(0x314) # Coupling type register
    XRFDC_FIFO_ENABLE = UIORegister(0x230) # FIFO Enable and Disable
    XRFDC_PLL_SDM_CFG0 = UIORegister(0x00) # PLL Configuration bits for sdm
    XRFDC_PLL_SDM_SEED0 = UIORegister(0x18) # PLL Bits for sdm LSB
    XRFDC_PLL_SDM_SEED1 = UIORegister(0x1C) # PLL Bits for sdm MSB
    XRFDC_PLL_VREG = UIORegister(0x44) # PLL bits for voltage regulator
    XRFDC_PLL_VCO0 = UIORegister(0x54) # PLL bits for coltage controlled oscillator LSB
    XRFDC_PLL_VCO1 = UIORegister(0x58) # PLL bits for coltage controlled oscillator MSB
    XRFDC_PLL_CRS1 = UIORegister(0x28) # PLL bits for coarse frequency control LSB
    XRFDC_PLL_CRS2 = UIORegister(0x2C) # PLL bits for coarse frequency control MSB
    XRFDC_PLL_DIVIDER0 = UIORegister(0x30) # PLL Output Divider LSB register
    XRFDC_PLL_DIVIDER1 = UIORegister(0x34) # PLL Output Divider MSB register
    XRFDC_PLL_SPARE0 = UIORegister(0x38) # PLL spare inputs LSB
    XRFDC_PLL_SPARE1 = UIORegister(0x3C) # PLL spare inputs MSB
    XRFDC_PLL_REFDIV = UIORegister(0x40) # PLL Reference Divider register
    XRFDC_PLL_VREG = UIORegister(0x44) # PLL voltage regulator
    XRFDC_PLL_CHARGEPUMP = UIORegister(0x48) # PLL bits for charge pumps
    XRFDC_PLL_LPF0 = UIORegister(0x4C) # PLL bits for loop filters LSB
    XRFDC_PLL_LPF1 = UIORegister(0x50) # PLL bits for loop filters MSB
    XRFDC_PLL_FPDIV = UIORegister(0x5C) # PLL Feedback Divider register
    XRFDC_CLK_NETWORK_CTRL0 = UIORegister(0x8C) # Clock network control and trim register
    XRFDC_CLK_NETWORK_CTRL1 = UIORegister(0x90) # Multi-tile sync and clock source control register

    """
    #XRFDC_ADC_FABRIC_RATE_TDD_OFFSET(X)                                                                            \
	((X == 0) ? XRFDC_ADC_FABRIC_RATE_OFFSET :                                                                     \
		    XRFDC_ADC_FABRIC_RATE_OBS_OFFSET)) # ADC Fabric Rate (or OBS) Register TDD Selected
    XRFDC_ADC_FABRIC_TDD_OFFSET(X)                                                                                 \
	((X == 0) ? XRFDC_ADC_FABRIC_OFFSET :                                                                          \
		    XRFDC_ADC_FABRIC_OBS_OFFSET)) # ADC Fabric Register (or OBS) TDD Selected*/
    XRFDC_ADC_FABRIC_DBG_TDD_OFFSET(X)                                                                             \
	((X == 0) ? XRFDC_ADC_FABRIC_DBG_OFFSET :                                                                      \
		    XRFDC_ADC_FABRIC_DBG_OBS_OFFSET)) # ADC Fabric Debug (or OBS) Register TDD Selected
    XRFDC_ADC_FIFO_LTNC_CRL_TDD_OFFSET(X)                                                                          \
	((X == 0) ?                                                                                                    \
		 XRFDC_ADC_FIFO_LTNC_CRL_OFFSET :                                                                      \
		 XRFDC_ADC_FIFO_LTNC_CRL_OBS_OFFSET)) # ADC FIFO Latency Control (or OBS) Register TDD Selected
    XRFDC_ADC_DECI_CONFIG_TDD_OFFSET(X)                                                                            \
	((X == 0) ? XRFDC_ADC_DECI_CONFIG_OFFSET :                                                                     \
		    XRFDC_ADC_DECI_CONFIG_OBS_OFFSET)) # ADC Decimation Config (or OBS) Register TDD Selected
    XRFDC_ADC_DECI_MODE_TDD_OFFSET(X)                                                                              \
	((X == 0) ? XRFDC_ADC_DECI_MODE_OFFSET :                                                                       \
		    XRFDC_ADC_DECI_MODE_OBS_OFFSET)) # ADC Decimation mode (or OBS) Register TDD Selected
    XRFDC_TDD_MODE0_OFFSET(X)                                                                                      \
	((X == 0) ? XRFDC_ADC_TDD_MODE0_OFFSET : XRFDC_DAC_TDD_MODE0_OFFSET)) # ADC TDD Mode 0 Configuration*/
    """
    pass
