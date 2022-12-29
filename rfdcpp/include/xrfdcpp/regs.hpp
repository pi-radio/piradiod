#pragma once

#include <stdint.h>

namespace rfdc {
  namespace csr {
    struct adc
    {
      // 0x0000
      uint32_t clk_en; /**< ADC Clock Enable Register */
      uint32_t adc_debug_rst; /**< ADC Debug Reset Register */
      uint32_t adc_fabric_rate; /**< ADC Fabric Rate Register */
      uint32_t adc_fabric; /**< ADC Fabric Register */
      // 0x0010
      uint32_t adc_fabric_isr; /**< ADC Fabric ISR Register */
      uint32_t adc_fabric_imr; /**< ADC Fabric IMR Register */
      uint32_t adc_fabric_dbg; /**< ADC Fabric Debug Register */
      uint32_t adc_update_dyn; /**< ADC Update Dynamic Register */
      // 0x0020
      uint32_t adc_fifo_ltnc_crl; /**< ADC FIFO Latency Control Register */
      uint32_t pad_0x0024[3];
      // 0x0030
      uint32_t adc_dec_isr; /**< ADC Decoder interface ISR Register */
      uint32_t adc_dec_imr; /**< ADC Decoder interface IMR Register */
      uint32_t datpath_isr; /**< ADC Data Path ISR Register */
      uint32_t datpath_imr; /**< ADC Data Path IMR Register */
      // 0x0040
      uint32_t adc_deci_config; /**< ADC Decimation Config Register */
      uint32_t adc_deci_mode; /**< ADC Decimation mode Register */
      uint32_t adc_deci_config_obs; /**< ADC Decimation Config Register */
      uint32_t adc_deci_mode_obs; /**< ADC Obs Decimation mode Register */
      // 0x0050
      uint32_t adc_fabric_rate_obs; /**< ADC Obs Fabric Rate Register */
      uint32_t adc_fabric_obs; /**< ADC Obs Fabric Register */
      uint32_t adc_fabric_dbg_obs; /**< ADC Obs Fabric Debug Register */
      uint32_t adc_fabric_isr_obs; /**< ADC Fabric ISR Observation Register */
      // 0x0060
      uint32_t adc_fabric_imr_obs; /**< ADC Fabric ISR Observation Register */
      uint32_t adc_fifo_ltnc_crl_obs; /**< ADC Obs FIFO Latency Control Register */
      uint32_t adc_tdd_mode0; /**< ADC TDD Mode 0 Configuration*/
      uint32_t pad_0x006c[5];
      // 0x0080
      uint32_t adc_mxr_cfg0; /**< ADC I channel mixer config Register */
      uint32_t adc_mxr_cfg1; /**< ADC Q channel mixer config Register */
      uint32_t mxr_mode; /**< ADC/DAC mixer mode Register */
      uint32_t nco_updt; /**< ADC/DAC NCO Update mode Register */
      // 0x0090
      uint32_t nco_rst; /**< ADC/DAC NCO Phase Reset Register */
      uint32_t adc_nco_fqwd_upp; /**< ADC NCO Frequency Word[47:32] Register */
      uint32_t adc_nco_fqwd_mid; /**< ADC NCO Frequency Word[31:16] Register */
      uint32_t adc_nco_fqwd_low; /**< ADC NCO Frequency Word[15:0] Register */
      // 0x00a0
      uint32_t nco_phase_upp; /**< ADC/DAC NCO Phase[17:16] Register */
      uint32_t nco_phase_low; /**< ADC/DAC NCO Phase[15:0] Register */
      uint32_t adc_nco_phase_mod; /**< ADC NCO Phase Mode Register */
      uint32_t pad_0x00ac[7];
      // 0x00c8
      uint32_t qmc_updt; /**< ADC/DAC QMC Update Mode Register */
      uint32_t qmc_cfg; /**< ADC/DAC QMC Config Register */
      // 0x00d0
      uint32_t qmc_off; /**< ADC/DAC QMC Offset Correction Register */
      uint32_t qmc_gain; /**< ADC/DAC QMC Gain Correction Register */
      uint32_t qmc_phase; /**< ADC/DAC QMC Phase Correction Register */
      uint32_t adc_crse_dly_updt; /**< ADC Coarse Delay Update Register */
      // 0x00e0
      uint32_t adc_crse_dly_cfg; /**< ADC Coarse delay Config Register */
      uint32_t adc_dat_scal_cfg; /**< ADC Data Scaling Config Register */
      uint32_t adc_switch_matrx; /**< ADC Switch Matrix Config Register */
      uint32_t adc_trshd0_cfg; /**< ADC Threshold0 Config Register */
      // 0x00f0
      uint32_t adc_trshd0_avg_up; /**< ADC Threshold0 Average[31:16] Register */
      uint32_t adc_trshd0_avg_lo; /**< ADC Threshold0 Average[15:0] Register */
      uint32_t adc_trshd0_under; /**< ADC Threshold0 Under Threshold Register */
      uint32_t adc_trshd0_over; /**< ADC Threshold0 Over Threshold Register */
      // 0x0100
      uint32_t adc_trshd1_cfg; /**< ADC Threshold1 Config Register */
      uint32_t adc_trshd1_avg_up; /**< ADC Threshold1 Average[31:16] Register */
      uint32_t adc_trshd1_avg_lo; /**< ADC Threshold1 Average[15:0] Register */
      uint32_t adc_trshd1_under; /**< ADC Threshold1 Under Threshold Register */
      // 0x0110
      uint32_t adc_trshd1_over; /**< ADC Threshold1 Over Threshold Register */
      uint32_t pad_0x0114[11];
      // 0x0140
      uint32_t adc_fend_dat_crl; /**< ADC Front end Data Control Register */
      uint32_t adc_ti_dcb_crl0; /**< ADC Time Interleaved digital correction block gain control0 Register */
      uint32_t adc_ti_dcb_crl1; /**< ADC Time Interleaved digital correction block gain control1 Register */
      uint32_t adc_ti_dcb_crl2; /**< ADC Time Interleaved digital correction block gain control2 Register */
      // 0x0150
      uint32_t adc_ti_dcb_crl3; /**< ADC Time Interleaved digital correction block gain control3 Register */
      uint32_t adc_ti_tisk_crl0; /**< ADC Time skew correction control bits0 Register */
      uint32_t adc_ti_tisk_crl1; /**< ADC Time skew correction control bits1 Register */
      uint32_t adc_ti_tisk_crl2; /**< ADC Time skew correction control bits2 Register */
      // 0x0160
      uint32_t adc_ti_tisk_crl3; /**< ADC Time skew correction control bits3 Register */
      uint32_t adc_ti_tisk_crl4; /**< ADC Time skew correction control bits4 Register */
      uint32_t adc_ti_tisk_dac0; /**< ADC Time skew DAC cal code of subadc ch0 Register(Below Gen 3) */
      uint32_t adc_ti_tisk_dac1; /**< ADC Time skew DAC cal code of subadc ch1 Register */
      // 0x0170
      uint32_t adc_ti_tisk_dac2; /**< ADC Time skew DAC cal code of subadc ch2 Register */
      uint32_t adc_ti_tisk_dac3; /**< ADC Time skew DAC cal code of subadc ch3 Register */
      uint32_t adc_ti_tisk_dacp0; /**< ADC Time skew DAC cal code of subadc ch0 Register */
      uint32_t adc_ti_tisk_dacp1; /**< ADC Time skew DAC cal code of subadc ch1 Register */
      // 0x0180
      uint32_t adc_ti_tisk_dacp2; /**< ADC Time skew DAC cal code of subadc ch2 Register */
      uint32_t adc_ti_tisk_dacp3; /**< ADC Time skew DAC cal code of subadc ch3 Register */
      uint32_t pad_0x0188[2];
      // 0x0190
      uint32_t data_scaler; /**< DAC Data Scaler Register */
      uint32_t pad_0x0194[1];
      uint32_t adc0_subdrp_addr; /**< subadc0, sub-drp address of target Register */
      uint32_t adc0_subdrp_dat; /**< subadc0, sub-drp data of target Register */
      // 0x01a0
      uint32_t adc1_subdrp_addr; /**< subadc1, sub-drp address of target Register */
      uint32_t adc1_subdrp_dat; /**< subadc1, sub-drp data of target Register */
      uint32_t adc2_subdrp_addr; /**< subadc2, sub-drp address of target Register */
      uint32_t adc2_subdrp_dat; /**< subadc2, sub-drp data of target Register */
      // 0x01b0
      uint32_t adc3_subdrp_addr; /**< subadc3, sub-drp address of target Register */
      uint32_t adc3_subdrp_dat; /**< subadc3, sub-drp data of target Register */
      uint32_t pad_0x01b8[2];
      // 0x01c0
      uint32_t adc_rx_mc_pwrdwn; /**< ADC Static configuration bits for ADC(RX) analog Register */
      uint32_t adc_dac_mc_cfg0; /**< ADC/DAC Static configuration bits for ADC/DAC analog Register */
      uint32_t adc_dac_mc_cfg1; /**< ADC/DAC Static configuration bits for ADC/DAC analog Register */
      uint32_t adc_dac_mc_cfg2; /**< ADC/DAC Static configuration bits for ADC/DAC analog Register */
      // 0x01d0
      uint32_t adc_rxpr_mc_cfg0; /**< ADC RX Pair static Configuration Register */
      uint32_t adc_rxpr_mc_cfg1; /**< ADC RX Pair static Configuration Register */
      uint32_t pad_0x01d8[10];
      // 0x0200
      uint32_t adc_ti_dcbsts0_bg; /**< ADC DCB Status0 BG Register */
      uint32_t adc_ti_dcbsts0_fg; /**< ADC DCB Status0 FG Register */
      uint32_t adc_ti_dcbsts1_bg; /**< ADC DCB Status1 BG Register */
      uint32_t adc_ti_dcbsts1_fg; /**< ADC DCB Status1 FG Register */
      // 0x0210
      uint32_t adc_ti_dcbsts2_bg; /**< ADC DCB Status2 BG Register */
      uint32_t adc_ti_dcbsts2_fg; /**< ADC DCB Status2 FG Register */
      uint32_t adc_ti_dcbsts3_bg; /**< ADC DCB Status3 BG Register */
      uint32_t adc_ti_dcbsts3_fg; /**< ADC DCB Status3 FG Register */
      // 0x0220
      uint32_t adc_ti_dcbsts4_mb; /**< ADC DCB Status4 MSB Register */
      uint32_t adc_ti_dcbsts4_lb; /**< ADC DCB Status4 LSB Register */
      uint32_t adc_ti_dcbsts5_mb; /**< ADC DCB Status5 MSB Register */
      uint32_t adc_ti_dcbsts5_lb; /**< ADC DCB Status5 LSB Register */
      // 0x0230
      uint32_t adc_ti_dcbsts6_mb; /**< ADC DCB Status6 MSB Register */
      uint32_t adc_ti_dcbsts6_lb; /**< ADC DCB Status6 LSB Register */
      uint32_t adc_ti_dcbsts7_mb; /**< ADC DCB Status7 MSB Register */
      uint32_t adc_ti_dcbsts7_lb; /**< ADC DCB Status7 LSB Register */
      uint32_t pad_0x0240[5];
      // 0x0254
      uint32_t dsa_updt; /**< ADC DSA Update Trigger REgister */
      uint32_t pad_0x0258[10];
      // 0x0280
      uint32_t adc_fifo_ltncy_lb; /**< ADC FIFO Latency measurement LSB Register */
      uint32_t adc_fifo_ltncy_mb; /**< ADC FIFO Latency measurement MSB Register */
      uint32_t pad_0x0288[32];
      // 0x0308
      uint32_t mb_config; /**< Multiband Config status */
      uint32_t pad_0x030c[61];
    } __attribute__((packed));

    struct dac
    {
      // 0x0000
      uint32_t clk_en; /**< ADC Clock Enable Register */
      uint32_t pad_0x0004[1];
      uint32_t dac_fabric_rate; /**< DAC Fabric Rate Register */
      uint32_t pad_0x000c[1];
      // 0x0010
      uint32_t dac_fifo_start; /**< DAC FIFO Start Register */
      uint32_t dac_fabric_isr; /**< DAC Fabric ISR Register */
      uint32_t dac_fabric_imr; /**< DAC Fabric IMR Register */
      uint32_t pad_0x001c[1];
      // 0x0020
      uint32_t dac_update_dyn; /**< DAC Update Dynamic Register */
      uint32_t pad_0x0024[4];
      // 0x0034
      uint32_t dac_datapath; /**< ADC Decoder interface IMR Register */
      uint32_t datpath_isr; /**< ADC Data Path ISR Register */
      uint32_t datpath_imr; /**< ADC Data Path IMR Register */
      // 0x0040
      uint32_t dac_interp_ctrl; /**< DAC Interpolation Control Register */
      uint32_t dac_iterp_data; /**< DAC interpolation data */
      uint32_t pad_0x0048[6];
      // 0x0060
      uint32_t dac_tdd_mode0; /**< DAC TDD Mode 0 Configuration*/
      uint32_t pad_0x0064[9];
      // 0x0088
      uint32_t mxr_mode; /**< ADC/DAC mixer mode Register */
      uint32_t nco_updt; /**< ADC/DAC NCO Update mode Register */
      // 0x0090
      uint32_t nco_rst; /**< ADC/DAC NCO Phase Reset Register */
      uint32_t pad_0x0094[3];
      // 0x00a0
      uint32_t nco_phase_upp; /**< ADC/DAC NCO Phase[17:16] Register */
      uint32_t nco_phase_low; /**< ADC/DAC NCO Phase[15:0] Register */
      uint32_t pad_0x00a8[6];
      // 0x00c0
      uint32_t dac_invsinc; /**< Invsinc control */
      uint32_t dac_mb_cfg; /**< Multiband config */
      uint32_t qmc_updt; /**< ADC/DAC QMC Update Mode Register */
      uint32_t qmc_cfg; /**< ADC/DAC QMC Config Register */
      // 0x00d0
      uint32_t qmc_off; /**< ADC/DAC QMC Offset Correction Register */
      uint32_t qmc_gain; /**< ADC/DAC QMC Gain Correction Register */
      uint32_t qmc_phase; /**< ADC/DAC QMC Phase Correction Register */
      uint32_t dac_crse_dly_cfg; /**< DAC Coarse delay Config Register */
      // 0x00e0
      uint32_t dac_crse_dly_updt; /**< DAC Coarse Delay Update Register */
      uint32_t pad_0x00e4[39];
      // 0x0180
      uint32_t dac_decoder_ctrl; /**< DAC Unary Decoder/ Randomizer settings */
      uint32_t dac_decoder_clk; /**< Decoder Clock enable */
      uint32_t pad_0x0188[2];
      // 0x0190
      uint32_t data_scaler; /**< DAC Data Scaler Register */
      uint32_t pad_0x0194[1];
      uint32_t dac_vop_ctrl; /**< DAC variable output power control Register */
      uint32_t pad_0x019c[10];
      // 0x01c4
      uint32_t dac_mc_cfg0; /**< Static Configuration  data for DAC Analog */
      uint32_t pad_0x01c8[2];
      // 0x01d0
      uint32_t dac_mc_cfg3; /**< DAC Static configuration bits for DAC analog Register */
      uint32_t pad_0x01d4[32];
      // 0x0254
      uint32_t dsa_updt; /**< ADC DSA Update Trigger REgister */
      uint32_t pad_0x0258[44];
      // 0x0308
      uint32_t mb_config; /**< Multiband Config status */
      uint32_t pad_0x030c[61];
    } __attribute__((packed));

    struct tile
    {
      uint32_t rsrved0000;
      uint32_t restart_posm;
      uint32_t restart_state;
      uint32_t current_state;
      uint32_t pad0010[(0x0038-0x0010)/4];
      uint32_t reset_count;
      uint32_t pad003C[(0x0080-0x0038)/4];
      uint32_t clock_detect;
      uint32_t pad0088[(0x0100-0x0088)/4];
      uint32_t post_impl_sim_speedup_reg;
      uint32_t pad0104[(0x0200-0x0104)/4];
      uint32_t isr;
      uint32_t ier;
      uint32_t conv0_intr;
      uint32_t conv0_intr_en;
      uint32_t conv1_intr;
      uint32_t conv1_intr_en;
      uint32_t conv2_intr;
      uint32_t conv2_intr_en;
      uint32_t conv3_intr;
      uint32_t conv3_intr_en;
      uint32_t common_status;
      uint32_t pad022C;
      uint32_t disable;
      uint32_t pad[(0x2000 - 0x0234)/4];
    } __attribute__((packed));


    const int max_slice = 4;

    struct dac_tile
    {
      tile t;
      dac dacs[max_slice];
      uint32_t pad[(0x2000-sizeof(dac)*max_slice)/4];  
    } __attribute__((packed));

    struct adc_tile
    {
      tile t;
      adc adcs[max_slice];
      uint32_t pad[(0x2000-sizeof(adc)*max_slice)/4];  
    } __attribute__((packed));


    struct rfdc
    {
      uint32_t version;
      uint32_t master_reset;
      uint32_t cisr;
      uint32_t cier;
      uint32_t pad[0x4000/4 - 4];
      dac_tile dac_tiles[4];
      adc_tile adc_tiles[4];
      uint32_t pad_0x24000[(0x40000-0x24000)/4];
    } __attribute__((packed));
  };
};

