cmake_minimum_required(VERSION 3.15)

# Required for CMAKE_MSVC_RUNTIME_LIBRARY (CMP0091)
cmake_policy(SET CMP0091 NEW)

project(QuantLibAddin CXX)

include(gensrc/cmake/commonSettings.cmake)

# Build the HTML documentation? Off by default; enable with -DBUILD_DOCS=ON.
option(BUILD_DOCS "Add targets to build the HTML documentation with Doxygen" OFF)

# -----------------------------------------------------------------------
# gensrc — optional code-generation step (the "Full" build).
# -----------------------------------------------------------------------
add_subdirectory(gensrc)

# -----------------------------------------------------------------------
# QuantLib
#
# QuantLib is built as part of this CMake build so its targets are
# available to QuantLibAddin.
# -----------------------------------------------------------------------

include(FetchContent)

set(QL_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(QL_BUILD_TEST_SUITE OFF CACHE BOOL "" FORCE)
set(QL_ENABLE_THREAD_SAFE_OBSERVER_PATTERN ON CACHE BOOL "" FORCE)
set(QL_ENABLE_SESSIONS ON CACHE BOOL "" FORCE)

FetchContent_Declare(
    QuantLib
    GIT_REPOSITORY https://github.com/lballabio/QuantLib.git
    GIT_TAG v1.43
)

FetchContent_MakeAvailable(QuantLib)

# QuantLib 1.43 creates ql_library. QuantLibAddin expects the
# namespaced target QuantLib::QuantLib.
if(TARGET ql_library AND NOT TARGET QuantLib::QuantLib)
    add_library(QuantLib::QuantLib ALIAS ql_library)
endif()

if(NOT TARGET QuantLib::QuantLib)
    message(FATAL_ERROR
        "QuantLib::QuantLib target was not created. "
        "Expected QuantLib target ql_library."
    )
endif()

# -----------------------------------------------------------------------
# Apply tagged layout postfixes to ql_library only, mirroring what
# QL_TAGGED_LAYOUT would have done, so the library filename matches
# the filenames expected by the hand-maintained VS build.
# -----------------------------------------------------------------------

if(MSVC)
    if(CMAKE_SIZEOF_VOID_P EQUAL 8)
        set(_ql_arch_tag "-x64")
    else()
        set(_ql_arch_tag "")
    endif()

    if(MSVC_LINK_DYNAMIC_RUNTIME)
        set(_ql_debug_postfix   "${_ql_arch_tag}-mt-gd")
        set(_ql_release_postfix "${_ql_arch_tag}-mt")
    else()
        set(_ql_debug_postfix   "${_ql_arch_tag}-mt-sgd")
        set(_ql_release_postfix "${_ql_arch_tag}-mt-s")
    endif()

    set_target_properties(ql_library PROPERTIES
        DEBUG_POSTFIX          "${_ql_debug_postfix}"
        RELEASE_POSTFIX        "${_ql_release_postfix}"
        RELWITHDEBINFO_POSTFIX "${_ql_release_postfix}"
        MINSIZEREL_POSTFIX     "${_ql_release_postfix}"
    )
endif()

# -----------------------------------------------------------------------
# ObjectHandler static libs (ohlib + ohxllib) and xlsdk
# -----------------------------------------------------------------------

add_subdirectory(ObjectHandler)

# -----------------------------------------------------------------------
# QuantLibObjects static lib (QuantLibAddin qlo wrapper)
# -----------------------------------------------------------------------

add_subdirectory(QuantLibAddin)

# -----------------------------------------------------------------------
# QuantLibXL — the Excel XLL (Windows only).
# -----------------------------------------------------------------------

add_subdirectory(QuantLibXL)

# -----------------------------------------------------------------------
# QuantLibAddinPython — QuantLibAddinPython
# -----------------------------------------------------------------------

add_subdirectory(Python)

# -----------------------------------------------------------------------
# Full build: make the addin libraries depend on gensrc.
# -----------------------------------------------------------------------

if(RUN_GENSRC)
    add_dependencies(ohlib ohgensrc)
    add_dependencies(QuantLibObjects qlgensrc)
endif()

# -----------------------------------------------------------------------
# Documentation
# -----------------------------------------------------------------------

if(BUILD_DOCS)
    add_custom_target(docs
        COMMENT
            "Building all HTML documentation "
            "(gensrc, ObjectHandler, QuantLibAddin, QuantLibXL)"
    )

    add_dependencies(docs
        gensrc-docs
        ObjectHandler-docs
        QuantLibAddin-docs
        QuantLibXL-docs
    )
endif()
