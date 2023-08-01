add_dependencies(${CURRENT_META} changelog.Debian.gz)

message(STATUS "Current meta: ${CURRENT_META}")
message(STATUS "Adding changelog for ${DEB_NAME} (${CURRENT_COMPONENT})")

add_custom_target(changelog.Debian.gz
  COMMENT "Compressing changelog"
  COMMAND echo gzip -n --best -c ${CMAKE_CURRENT_SOURCE_DIR}/CHANGELOG
  COMMAND echo  ${CMAKE_CURRENT_BINARY_DIR}/${CHANGELOG_FILE}
  COMMAND gzip -n --best -c ${CMAKE_CURRENT_SOURCE_DIR}/CHANGELOG > ${CMAKE_CURRENT_BINARY_DIR}/changelog.Debian.gz
  DEPENDS "CHANGELOG")


install(FILES ${CMAKE_CURRENT_BINARY_DIR}/changelog.Debian.gz
  DESTINATION usr/share/doc/${DEB_NAME}
  COMPONENT ${CURRENT_COMPONENT}
  PERMISSIONS ${STANDARD_DOC_PERM})

