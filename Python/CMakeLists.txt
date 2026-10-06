cmake_minimum_required(VERSION 3.20)

project(QuantLibAddinPython LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# -----------------------------------------------------------------------
# Python
# -----------------------------------------------------------------------

find_package(Python COMPONENTS Interpreter Development REQUIRED)

# -----------------------------------------------------------------------
# pybind11
# -----------------------------------------------------------------------

execute_process(
    COMMAND ${Python_EXECUTABLE} -m pybind11 --cmakedir
    OUTPUT_VARIABLE pybind11_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

find_package(pybind11 CONFIG REQUIRED)

# -----------------------------------------------------------------------
# QuantLib
#
# When Python is built as part of the main QuantLibAddin project,
# QuantLib::QuantLib is already available from FetchContent.
#
# When Python is configured standalone, fall back to an installed
# QuantLib package.
# -----------------------------------------------------------------------

if(NOT TARGET QuantLib::QuantLib)
    find_package(QuantLib CONFIG REQUIRED)
endif()

if(NOT TARGET QuantLib::QuantLib)
    message(FATAL_ERROR
        "QuantLib::QuantLib target is not available"
    )
endif()

# -----------------------------------------------------------------------
# Verify QuantLibAddin / ObjectHandler targets
# -----------------------------------------------------------------------

if(NOT TARGET QuantLibObjects)
    message(FATAL_ERROR
        "QuantLibObjects target is not available. "
        "Make sure Python is added after QuantLibAddin."
    )
endif()

if(NOT TARGET ohlib)
    message(FATAL_ERROR
        "ohlib target is not available. "
        "Make sure Python is added after ObjectHandler."
    )
endif()

# -----------------------------------------------------------------------
# Python module
# -----------------------------------------------------------------------

pybind11_add_module(
    quantlib_addin
    bindings/QuantLibAddinCpp.cpp
)

# -----------------------------------------------------------------------
# Include directories
#
# These are kept explicitly here so the Python binding can find the
# QuantLibAddin and ObjectHandler headers even if those targets do not
# yet publish their include directories as PUBLIC.
# -----------------------------------------------------------------------

target_include_directories(
    quantlib_addin
    PRIVATE

        # QuantLibAddin C++ headers
        ${CMAKE_CURRENT_SOURCE_DIR}/../QuantLibAddin/Addins/Cpp

        # ObjectHandler headers
        # Required for:
        #   #include <oh/property.hpp>
        #   #include <oh/repository.hpp>
        ${CMAKE_CURRENT_SOURCE_DIR}/../ObjectHandler
)

# -----------------------------------------------------------------------
# Libraries
# -----------------------------------------------------------------------

target_link_libraries(
    quantlib_addin
    PRIVATE

        # QuantLibAddin wrapper implementation
	AddinCpp
        QuantLibObjects

        # ObjectHandler
        ohlib

        # QuantLib
        QuantLib::QuantLib
)

# -----------------------------------------------------------------------
# Output
# -----------------------------------------------------------------------

set_target_properties(
    quantlib_addin
    PROPERTIES
        OUTPUT_NAME "quantlib_addin"
)
