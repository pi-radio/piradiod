message(STATUS "Adding copyright for ${DEB_NAME} (${CURRENT_COMPONENT})")

install(FILES copyright
  DESTINATION usr/share/doc/${DEB_NAME}/
  COMPONENT ${CURRENT_COMPONENT}
  PERMISSIONS ${STANDARD_DOC_PERM})
