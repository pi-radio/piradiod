#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <xrfdcpp/xrfdcpp.hpp>

namespace py = pybind11;
using namespace rfdc;

PYBIND11_MODULE(xrfdcpy, m) {
  m.doc() = "Python bindings for the Xilinx RFDC";

  py::class_<ADC>(m, "ADC")
    ;

  py::class_<DAC>(m, "DAC")
    ;
  
  py::class_<ADCTile>(m, "ADCTile")
    ;

  py::class_<DACTile>(m, "DACTile")
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
