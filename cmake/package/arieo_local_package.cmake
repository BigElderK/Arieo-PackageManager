
function(arieo_add_local_package)
    cmake_parse_arguments(ARG "" "LOCAL_PACKAGE_PATH;OUT_PACKAGE_DIR" "" ${ARGN})

    message(STATUS "Adding local package: 
        PACKAGE_PATH=${ARG_LOCAL_PACKAGE_PATH}
    ")

    # check if there is a CMakeLists.txt in the source dir
    if(NOT EXISTS "${ARG_LOCAL_PACKAGE_PATH}/CMakeLists.txt")
        message(FATAL_ERROR "Local package source directory ${ARG_LOCAL_PACKAGE_PATH} does not contain a CMakeLists.txt file.")
    endif()

    # add_subdirectory(
    #     ${ARG_LOCAL_PACKAGE_PATH}
    # )
    # Get the package name from the CMakeLists.txt file in the local package directory
    # return the CMakeLists.txt path of the local package
    set(${ARG_OUT_PACKAGE_DIR} "${ARG_LOCAL_PACKAGE_PATH}" PARENT_SCOPE)
endfunction()
