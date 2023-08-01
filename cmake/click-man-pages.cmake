macro(generate_click_man_pages command component)
  execute_process(COMMAND ${SCRIPT_DIR}/get-click-man-pages ${CMAKE_CURRENT_SOURCE_DIR}/${command}
    OUTPUT_VARIABLE GENERATED_MAN_PAGES)
  
  string(STRIP "${GENERATED_MAN_PAGES}" GENERATED_MAN_PAGES)
  string(REPLACE "\n" ";" GENERATED_MAN_PAGES ${GENERATED_MAN_PAGES})

  message(STATUS "Generating manual pages: ${GENERATED_MAN_PAGES}")
  
  add_custom_target(compressed_man_pages)

  add_custom_command(OUTPUT ${GENERATED_MAN_PAGES}
    COMMENT "Generating man pages"
    COMMAND ${SCRIPT_DIR}/write-click-man-pages ${CMAKE_CURRENT_SOURCE_DIR}/${command} ${CMAKE_CURRENT_BINARY_DIR}
    DEPENDS ${command}
    )

  foreach(file IN LISTS GENERATED_MAN_PAGES)
    message(STATUS "Man page ${file}")
    add_custom_target("${file}.gz"
      COMMAND gzip -n --best -c ${CMAKE_CURRENT_BINARY_DIR}/${file} > ${CMAKE_CURRENT_BINARY_DIR}/${file}.gz
      DEPENDS "${file}")
  
    add_dependencies(compressed_man_pages "${file}.gz")

    install(FILES ${CMAKE_CURRENT_BINARY_DIR}/${file}.gz
      DESTINATION usr/share/man/man1/
      COMPONENT ${component}
      PERMISSIONS ${STANDARD_DOC_PERM})
  endforeach()
endmacro()
