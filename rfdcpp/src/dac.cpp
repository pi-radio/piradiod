#include <xrfdcpp/dac.hpp>

using namespace rfdc;

DAC::DAC(types::tile_t &_tile, int _n,
    const types::acfg_t &_acfg,
    const types::dcfg_t &_dcfg,
    types::csr_t _csr) : DACSlice(_tile, _n,
				  _acfg, _dcfg,
				  _csr)
{
}


nyquist_zone DAC::get_nyquist_zone(void)
{
  auto mb = tile.get_multiband_mode();

  
#if 0
  if (MultibandConfig != XRFDC_MB_MODE_SB) {
    Status = XRFdc_CheckDigitalPathEnabled(InstancePtr, Type, Tile_Id, Block_Id);
  } else {
    Status = XRFdc_CheckBlockEnabled(InstancePtr, Type, Tile_Id, Block_Id);
  }
  
  if (Status != XRFDC_SUCCESS) {
    metal_log(METAL_LOG_ERROR, "\n %s %u block %u not available in %s\r\n",
	      (Type == XRFDC_ADC_TILE) ? "ADC" : "DAC", Tile_Id, Block_Id, __func__);
    goto RETURN_PATH;
  }
  
  Block = Block_Id;
  if ((XRFdc_IsHighSpeedADC(InstancePtr, Tile_Id) == 1) && (Block_Id == XRFDC_BLK_ID1) &&
      (Type == XRFDC_ADC_TILE)) {
    Block_Id = XRFDC_BLK_ID2;
  }
  
  BaseAddr = XRFDC_BLOCK_BASE(Type, Tile_Id, Block_Id);

  if (Type == XRFDC_ADC_TILE) {
    /* Identify calibration mode */
    Status = XRFdc_GetCalibrationMode(InstancePtr, Tile_Id, Block, &CalibrationMode);
    if (Status != XRFDC_SUCCESS) {
      return XRFDC_FAILURE;
    }
    ReadReg = XRFdc_RDReg(InstancePtr, BaseAddr, XRFDC_ADC_TI_TISK_CRL0_OFFSET, XRFDC_TI_TISK_ZONE_MASK);
    *NyquistZonePtr = (ReadReg >> XRFDC_TISK_ZONE_SHIFT);
  } else {
    ReadReg = XRFdc_RDReg(InstancePtr, BaseAddr, XRFDC_DAC_MC_CFG0_OFFSET, XRFDC_MC_CFG0_MIX_MODE_MASK);
    *NyquistZonePtr = (ReadReg >> XRFDC_MC_CFG0_MIX_MODE_SHIFT);
  }
  if (*NyquistZonePtr == 0U) {
    *NyquistZonePtr = XRFDC_ODD_NYQUIST_ZONE;
  } else {
    *NyquistZonePtr = XRFDC_EVEN_NYQUIST_ZONE;
  }
  if (InstancePtr->RFdc_Config.IPType < XRFDC_GEN3) {
    if ((Type == XRFDC_ADC_TILE) && (CalibrationMode == XRFDC_CALIB_MODE1)) {
      if (*NyquistZonePtr == XRFDC_EVEN_NYQUIST_ZONE) {
	*NyquistZonePtr = XRFDC_ODD_NYQUIST_ZONE;
      } else {
	*NyquistZonePtr = XRFDC_EVEN_NYQUIST_ZONE;
      }
    }
  }
#endif
}

DACTile::DACTile(RFDC &_dc,
		 int _n,
		 const cfg::dac &_conf,
		 volatile csr::dac_tile *_csr) : Tile(&_csr->t, _n, _conf),
						 conf(_conf),
						 csr(_csr),
						 dc(_dc)
{
  int nslices = dc.get_n_dac_slices();
    
  slices.reserve(nslices);

  for (int i = 0; i < nslices; i++) {
    slices.emplace_back(new DAC(*this, i, conf.analog[i], conf.digital[i], &csr->dacs[i]));
  }
  
}

bool DACTile::is_enabled(void) {
  return bitfield(4 + n_tile, 1).get(dc.get_tiles_enabled_mask());
}

uint32_t DACTile::get_path_enabled_reg(void) {
  return dc.get_dac_paths_enabled();
}


