#[[
    Arieo Local Package - CMake Module
    
    Usage:
        arieo_add_local_package(
            NAME            <package_name>
            SOURCE_DIR      <source_directory>
        )
]]

include_guard(GLOBAL)
include(ExternalProject)

function(arieo_add_local_package)
    cmake_parse_arguments(ARG "" "SOURCE_DIR" "" ${ARGN})

    message(STATUS "Adding local package: 
        SOURCE_DIR=${ARG_SOURCE_DIR}
    ")

    # check if there is a CMakeLists.txt in the source dir
    if(NOT EXISTS "${ARG_SOURCE_DIR}/CMakeLists.txt")
        message(FATAL_ERROR "Local package source directory ${ARG_SOURCE_DIR} does not contain a CMakeLists.txt file.")
    endif()

    include ("${ARG_SOURCE_DIR}/CMakeLists.txt")
endfunction()
