#[[
    Arieo Remote Package - CMake Module
    
    Usage:
        arieo_add_remote_package(
            NAME            <package_name>
            GIT_REPOSITORY  <git_url>
            GIT_TAG         <branch_or_tag>
            SOURCE_DIR      <source_directory>
            BINARY_DIR      <binary_directory>
        )
]]

include(ExternalProject)

cmake_minimum_required(VERSION 3.11)

include(FetchContent)

function(arieo_add_remote_package)
    cmake_parse_arguments(ARG 
        ""
        "GIT_REPOSITORY;GIT_TAG;" 
        "" 
        ${ARGN}
    )

    # Get package name from git repository URL (last part of URL, strip .git if present)
    string(REGEX MATCH ".*/([^/]+)$" _match "${ARG_GIT_REPOSITORY}")
    if(_match)
        set(package_name "${CMAKE_MATCH_1}")
        string(REGEX REPLACE "\\.git$" "" package_name "${package_name}")
    else()
        message(FATAL_ERROR "Could not extract package name from git repository URL: ${ARG_GIT_REPOSITORY}")
    endif()

    message(STATUS "Adding remote package: 
        GIT_REPOSITORY=${ARG_GIT_REPOSITORY}
        GIT_TAG=${ARG_GIT_TAG}"
    )
    
    # download source from git repository to source dir
    FetchContent_Declare(
        ${package_name}
        GIT_REPOSITORY ${ARG_GIT_REPOSITORY}
        GIT_TAG ${ARG_GIT_TAG}
        GIT_SHALLOW    TRUE
        SOURCE_DIR     $ENV{ARIEO_PACKAGES_REMOTE_SOURCE_DIR}/${package_name}
    )
    FetchContent_Populate(${package_name})

    message(STATUS "Adding remote package: 
        GIT_REPOSITORY=${ARG_GIT_REPOSITORY}
        GIT_TAG=${ARG_GIT_TAG}
        SOURCE_DIR=$ENV{ARIEO_PACKAGES_REMOTE_SOURCE_DIR}/${package_name}
        BINARY_DIR=$ENV{ARIEO_PACKAGES_BUILD_OUTPUT_DIR}/${package_name}
        INSTALL_DIR=$ENV{ARIEO_PACKAGES_INSTALL_DIR}/${package_name}
    ")

    # ExternalProject_Add(${ARG_NAME}
    #     GIT_REPOSITORY      ${ARG_GIT_REPOSITORY}
    #     GIT_TAG             ${ARG_GIT_TAG}
    #     GIT_SHALLOW         ON
    #     SOURCE_DIR          $ENV{ARIEO_PACKAGES_REMOTE_SOURCE_DIR}/${package_name}
    #     BINARY_DIR          $ENV{ARIEO_PACKAGES_REMOTE_BINARY_DIR}/${package_name}
    #     UPDATE_DISCONNECTED ON
    #     INSTALL_COMMAND     ""
    # )
endfunction()


