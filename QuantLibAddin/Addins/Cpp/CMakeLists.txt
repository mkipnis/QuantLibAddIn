# QuantLibAddin/Addins/Cpp/CMakeLists.txt
# Builds the AddinCpp static library (the C++ addin layer).

file(GLOB ADDIN_CPP_SOURCES
    CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/*.cpp"
)

add_library(AddinCpp STATIC
    ${ADDIN_CPP_SOURCES}
)

target_include_directories(AddinCpp PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../..>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../../../ObjectHandler>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../../../QuantLib>
)

target_compile_definitions(AddinCpp PRIVATE
    _LIB
)

target_link_libraries(AddinCpp PUBLIC
    QuantLibObjects
)
