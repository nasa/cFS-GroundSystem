# CMake snippet for building cmdUtil 

if (ENABLE_DATA_DICTIONARY)
  include_directories(${msglib_MISSION_DIR}/inc)
endif()

add_executable(cmdUtil cmdUtil.c SendUdp.c)

if (ENABLE_DATA_DICTIONARY)
  target_link_libraries(cmdUtil cfe_mission_dictionary msglib_full)
endif()

install(TARGETS cmdUtil DESTINATION host)


