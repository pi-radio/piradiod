#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <xrfdcpp/mixer.hpp>
#include <xrfdcpp/xrfdcpp.hpp>

namespace py = pybind11;
using namespace rfdc;

PYBIND11_MODULE(xrfdcpy, m) {
  m.doc() = "Python bindings for the Xilinx RFDC";

  py::class_<frequency<double>>(m, "Frequency")
    ;
  
  py::class_<mixer::Mixer<ADCSliceTypes>>(m, "ADCMixer")
    ;

  py::class_<mixer::Mixer<DACSliceTypes>>(m, "DACMixer")
    ;

  
  py::class_<ADC, std::shared_ptr<ADC>>(m, "ADC")
    .def_readonly("mixer", &ADC::mixer)
    .def_property_readonly("is_high_speed", &ADC::is_high_speed)
    .def_property_readonly("sampling_rate", &ADC::get_sampling_rate)
    ;

  py::class_<DAC, std::shared_ptr<DAC>>(m, "DAC")
    .def_readonly("mixer", &DAC::mixer)
    ;
  
  py::class_<ADCTile, std::shared_ptr<ADCTile>>(m, "ADCTile")
    .def_property_readonly("slices", &ADCTile::get_slices)
    ;

  py::class_<DACTile, std::shared_ptr<DACTile>>(m, "DACTile")
    .def_property_readonly("slices", &DACTile::get_slices)
    ;
  
  py::class_<RFDC>(m, "RFDC")
    .def(py::init())
    .def_property_readonly("adc_tiles", &RFDC::get_adc_tiles)
    .def_property_readonly("dac_tiles", &RFDC::get_dac_tiles)
    .def_property_readonly("adcs", &RFDC::get_adcs)
    .def_property_readonly("dacs", &RFDC::get_dacs)
    .def_property_readonly("ip_version", &RFDC::version)
    ;
}
