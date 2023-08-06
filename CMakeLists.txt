
cmake_minimum_required(VERSION 3.8)

project(piradio)

include(GNUInstallDirs)

set(USE_CPACK 1)

foreach(name IN ITEMS base libpiradio libtilmx libsamplebuf sampled fpgad zcu111d rfdcd)
  message(STATUS "Adding ${name}")
  add_subdirectory("${name}")
endforeach()  


if (USE_CPACK)
  set(CPACK_SET_DESTDIR true)
  set(CPACK_INSTALL_PREFIX /)
  set(CPACK_GENERATOR DEB)
  set(CPACK_PACKAGE_NAME "piradio")
  set(CPACK_PACKAGE_VENDOR "Pi Radio Inc.")
  set(CPACK_PACKAGE_CONTACT "Michael Zappe <zapman@pi-rad.io>")
  set(CPACK_DEBIAN_PACKAGE_VERSION 0.1.2)
  set(CPACK_DEBIAN_PACKAGE_RELEASE 7)
  set(CPACK_DEBIAN_PACKAGE_CONTROL_EXTRA "${CMAKE_CURRENT_SOURCE_DIR}/deb/postinst")
  set(CPACK_COMPONENTS_GROUPING ONE_PER_GROUP)
  set(CPACK_DEB_PACKAGE_COMPONENT ON)
  set(CPACK_DEB_COMPONENT_INSTALL ON)
  set(CPACK_DEBIAN_FILE_NAME "DEB-DEFAULT")
  set(CPACK_DEBIAN_ENABLE_COMPONENT_DEPENDS ON)
  set(CPACK_DEBIAN_DEBUGINFO_PACKAGE ON)

  set(CPACK_DEBIAN_PACKAGE_DEBUG ON)
  
  set(CPACK_DEBIAN_PACKAGE_DESCRIPTION "Global Pi Radio Description")
  set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "Global Pi Radio Description Summary")
  
  #
  # base installation variables
  #  
  #set(CPACK_DEBIAN_BASE_DISPLAY_NAME "piradio-base")
  set(CPACK_COMPONENT_BASE_DESCRIPTION "Pi Radio base files")
  set(CPACK_DEBIAN_BASE_DESCRIPTION "Pi Radio base files")
  set(CPACK_DEBIAN_BASE_PACKAGE_DEPENDS "python3(>=3.10.6)")
  set(CPACK_DEBIAN_BASE_PACKAGE_CONTROL_EXTRA "${CMAKE_CURRENT_SOURCE_DIR}/base/deb/conffiles;${CMAKE_CURRENT_SOURCE_DIR}/base/deb/postinst")
  message(STATUS "base package control: ${CPACK_DEBIAN_BASE_PACKAGE_CONTROL_EXTRA}")
  
  #
  # fpgad installation variables
  #
  #set(CPACK_COMPONENT_FPGAD_DISPLAY_NAME "piradio-fpgad")
  #set(CPACK_COMPONENT_FPGAD_DESCRIPTION "Pi Radio FPGA mangement daemon")

  piradio_service_deb(FPGAD "Pi Radio FPGA mangement daemon")
  piradio_service_deb(ZCU111D "Pi Radio ZCU111 mangement daemon")
  piradio_service_deb(RFDCD "Pi Radio RFDC mangement daemon")
  piradio_service_deb(SAMPLED "Pi Radio non-realtime sample capture daemon")
  
  set(CPACK_COMPONENTS_ALL BASE FPGAD ZCU111D RFDCD SAMPLED)
  
endif()


if (USE_CPACK)
  include(CPack)
endif()

message(STATUS "All components: ${CPACK_COMPONENTS_ALL}")

if(1)
  get_cmake_property(_variableNames VARIABLES)
  list (SORT _variableNames)
  foreach (_variableName ${_variableNames})
    message(STATUS "${_variableName}=${${_variableName}}")
  endforeach()
endif()
