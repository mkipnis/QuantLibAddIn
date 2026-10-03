# QuantLibAddin/Clients/Cpp/CMakeLists.txt
# Builds the Swap console executable (C++ addin demo client).
#
# Output naming mirrors Build A:
#   Swap-v<toolset>-x64-mt[-s|-gd|-sgd]-1_42_0.exe
#
# The executable is written to  build/<preset>/cpp/
# which keeps it separate from the Build A output in
# QuantLibAddin/Clients/Cpp/bin/.

# -----------------------------------------------------------------------
# Toolset / platform / runtime tags  (same logic as QuantLibXL)
# -----------------------------------------------------------------------
# The leading hyphen is part of the toolset tag so that it disappears together
# with the tag on non-MSVC toolchains (gcc/clang have no toolset tag); this
# avoids an orphaned separator, e.g. "Swap--x64" on Linux.
if(MSVC)
    set(SWAP_TOOLSET_TAG "-v${MSVC_TOOLSET_VERSION}")
else()
    set(SWAP_TOOLSET_TAG "")
endif()

if(CMAKE_SIZEOF_VOID_P EQUAL 8)
    set(SWAP_PLATFORM_TAG "-x64")
else()
    set(SWAP_PLATFORM_TAG "")
endif()

if(MSVC_LINK_DYNAMIC_RUNTIME)
    set(SWAP_RELEASE_RUNTIME_TAG "-mt")
    set(SWAP_DEBUG_RUNTIME_TAG   "-mt-gd")
else()
    set(SWAP_RELEASE_RUNTIME_TAG "-mt-s")
    set(SWAP_DEBUG_RUNTIME_TAG   "-mt-sgd")
endif()

set(SWAP_VERSION_TAG "1_42_0")

set(SWAP_BASE_NAME
    "Swap${SWAP_TOOLSET_TAG}${SWAP_PLATFORM_TAG}"
)

# -----------------------------------------------------------------------
# Executable target
# -----------------------------------------------------------------------
add_executable(Swap swap_out.cpp)

set_target_properties(Swap PROPERTIES
    OUTPUT_NAME
        "${SWAP_BASE_NAME}$<$<CONFIG:Debug>:${SWAP_DEBUG_RUNTIME_TAG}>$<$<NOT:$<CONFIG:Debug>>:${SWAP_RELEASE_RUNTIME_TAG}>-${SWAP_VERSION_TAG}"
    RUNTIME_OUTPUT_DIRECTORY             "${CMAKE_BINARY_DIR}/cpp"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE     "${CMAKE_BINARY_DIR}/cpp"
    RUNTIME_OUTPUT_DIRECTORY_DEBUG       "${CMAKE_BINARY_DIR}/cpp"
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${CMAKE_BINARY_DIR}/cpp"
    RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL  "${CMAKE_BINARY_DIR}/cpp"
)

target_include_directories(Swap PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../..
    ${CMAKE_CURRENT_SOURCE_DIR}/../../../ObjectHandler
    ${CMAKE_CURRENT_SOURCE_DIR}/../../../QuantLib
)

target_link_libraries(Swap PRIVATE
    AddinCpp
)

if(WIN32)
    target_link_libraries(Swap PRIVATE
        odbc32
        odbccp32
        Ws2_32
        advapi32
    )
endif()
