include(../cmake/piradio.cmake)

piradio_project("piradio-base" BASE)

include(${MACRO_DIR}/changelog.cmake)
include(${MACRO_DIR}/copyright.cmake)
include(${MACRO_DIR}/click-man-pages.cmake)

generate_click_man_pages(src/piradio-admin BASE)

add_dependencies(${CURRENT_META} compressed_man_pages)

install(FILES src/piradio-admin
  DESTINATION usr/bin
  COMPONENT BASE
  PERMISSIONS ${STANDARD_EXE_PERM})

install(FILES conf/spidev.conf
  DESTINATION etc/modules-load.d
  COMPONENT BASE
  PERMISSIONS ${STANDARD_CONF_PERM})

install(FILES conf/40-piradio.rules
  DESTINATION lib/udev/rules.d
  COMPONENT BASE
  PERMISSIONS ${STANDARD_CONF_PERM})
