import argparse
import os
from pathlib import Path

from clang import cindex
from clang.cindex import CursorKind


NAMESPACE = "QuantLibAddinCpp"


def configure_clang(libclang=None):
    if libclang:
        cindex.Config.set_library_file(libclang)
        return

    if path := os.getenv("LIBCLANG_PATH"):
        cindex.Config.set_library_file(path)
    elif path := os.getenv("LIBCLANG_DIR"):
        cindex.Config.set_library_path(path)


def namespaces(cursor):
    result = []
    parent = cursor.semantic_parent

    while parent:
        if parent.kind == CursorKind.TRANSLATION_UNIT:
            break

        if parent.kind == CursorKind.NAMESPACE and parent.spelling:
            result.append(parent.spelling)

        parent = parent.semantic_parent

    return result[::-1]


def qualified_name(cursor):
    parts = namespaces(cursor)

    if cursor.spelling:
        parts.append(cursor.spelling)

    return "::".join(parts)


def is_target_function(cursor):
    if cursor.kind != CursorKind.FUNCTION_DECL:
        return False

    if not cursor.spelling:
        return False

    ns = namespaces(cursor)

    return bool(ns) and ns[-1] == NAMESPACE


def collect_functions(cursor, result):
    if is_target_function(cursor):
        result.append(cursor)
        return

    for child in cursor.get_children():
        collect_functions(child, result)


def dump_function(cursor):
    """Debug helper for inspecting what Clang actually parsed."""

    print()
    print("=" * 80)
    print("FUNCTION")
    print("=" * 80)

    print("Qualified name:")
    print(f"  {qualified_name(cursor)}")

    print("Location:")
    print(f"  {cursor.location.file}")
    print(f"  line={cursor.location.line}")
    print(f"  column={cursor.location.column}")

    print("Function type:")
    print(f"  {cursor.type.spelling}")

    print("Display name:")
    print(f"  {cursor.displayname}")

    print()
    print("Parameters:")

    for i, param in enumerate(cursor.get_arguments()):
        print(f"  [{i}] {param.spelling}")
        print(f"      display:  {param.displayname}")
        print(f"      type:     {param.type.spelling}")
        print(f"      canonical:{param.type.get_canonical().spelling}")
        print(f"      kind:     {param.type.kind}")

        decl = param.type.get_declaration()

        if decl:
            print(f"      decl:     {decl.spelling}")
            print(f"      declkind: {decl.kind}")

    print()


def function_key(cursor):
    """
    Used to remove duplicate declarations.
    """
    return (
        qualified_name(cursor),
        tuple(
            arg.type.get_canonical().spelling
            for arg in cursor.get_arguments()
        ),
    )


def generate_binding(cursor):
    return (
        f'    m.def("{cursor.spelling}", '
        f'&{qualified_name(cursor)});'
    )


def parse_header(index, header, clang_args):
    """
    Parse one header and report diagnostics.
    """

    try:
        tu = index.parse(
            str(header),
            args=clang_args,
            options=cindex.TranslationUnit.PARSE_INCOMPLETE,
        )

    except Exception as exc:
        print(
            f"WARNING: failed to parse {header}: {exc}"
        )
        return None

    # Always report serious diagnostics.
    for diagnostic in tu.diagnostics:
        if diagnostic.severity >= diagnostic.Error:
            print(
                f"CLANG ERROR: {header}: "
                f"{diagnostic}"
            )

    return tu


def main():
    parser = argparse.ArgumentParser(
        description="Generate plain 1-to-1 pybind11 bindings."
    )

    parser.add_argument(
        "directory",
        help="Directory containing QuantLibAddin C++ headers",
    )

    parser.add_argument(
        "output",
        help="Generated C++ output file",
    )

    parser.add_argument(
        "--module",
        default="quantlib_addin",
        help="Python module name",
    )

    parser.add_argument(
        "--include",
        action="append",
        default=[],
        help="Additional Clang include directory",
    )

    parser.add_argument(
        "--clang-arg",
        action="append",
        default=[],
        help="Additional argument passed directly to Clang",
    )

    parser.add_argument(
        "--std",
        default="c++17",
        help="C++ standard",
    )

    parser.add_argument(
        "--libclang",
        help="Path to libclang",
    )

    parser.add_argument(
        "--debug-function",
        action="append",
        default=[],
        help="Print detailed AST information for this function",
    )

    args = parser.parse_args()

    root = Path(args.directory).resolve()
    output = Path(args.output)

    configure_clang(args.libclang)

    headers = sorted(root.rglob("*.hpp"))

    # ------------------------------------------------------------------
    # Clang arguments
    # ------------------------------------------------------------------

    clang_args = [
        "-x",
        "c++",
        f"-std={args.std}",

        # Important:
        # Make the QuantLibAddin header tree visible to Clang.
        f"-I{root}",
        f"-I{root.parent / '../../ObjectHandler'}",

        # Avoid stopping after the first error.
        "-ferror-limit=0",
    ]

    # User supplied include directories.
    clang_args.extend(
        f"-I{Path(include).resolve()}"
        for include in args.include
    )

    # Additional user supplied Clang arguments.
    clang_args.extend(args.clang_arg)

    print("Clang arguments:")
    for arg in clang_args:
        print(f"  {arg}")

    print()

    index = cindex.Index.create()

    functions = []

    # ------------------------------------------------------------------
    # Parse headers
    # ------------------------------------------------------------------

    for header in headers:

        tu = parse_header(
            index,
            header,
            clang_args,
        )

        if tu is None:
            continue

        collect_functions(
            tu.cursor,
            functions,
        )

    # ------------------------------------------------------------------
    # Remove duplicate declarations.
    # ------------------------------------------------------------------

    unique = {}

    for function in functions:
        unique[function_key(function)] = function

    functions = list(unique.values())

    # ------------------------------------------------------------------
    # Optional debugging
    # ------------------------------------------------------------------

    if args.debug_function:

        for function in functions:
            if function.spelling in args.debug_function:
                dump_function(function)

    # ------------------------------------------------------------------
    # Sort functions
    # ------------------------------------------------------------------

    functions.sort(
        key=lambda f: (
            f.spelling,
            qualified_name(f),
        )
    )

    # ------------------------------------------------------------------
    # Generate C++
    # ------------------------------------------------------------------

    lines = [
        "#include <pybind11/pybind11.h>",
        "#include <pybind11/stl.h>",
        "",
    ]

    # Include all headers so the generated function pointers are visible.
    for header in headers:
        relative = header.relative_to(root)

        lines.append(
            f'#include "{relative}"'
        )

    cpp_code = r'''
    py::class_<ObjectHandler::property_t>(m, "Property")
    // Empty / missing property
    .def(py::init<>())

    // Scalar values
    .def_static("from_bool", [](bool value) {
        return ObjectHandler::property_t(value);
    })
    .def_static("from_int", [](int value) {
        return ObjectHandler::property_t(value);
    })
    .def_static("from_long", [](long value) {
        return ObjectHandler::property_t(value);
    })
    .def_static("from_double", [](double value) {
        return ObjectHandler::property_t(value);
    })
    .def_static("from_string", [](const std::string& value) {
        return ObjectHandler::property_t(value);
    })

    // Vector values
    .def_static("from_bool_vector", [](const std::vector<bool>& value) {
        return ObjectHandler::property_t(value);
    })
    .def_static("from_int_vector", [](const std::vector<int>& value) {
        return ObjectHandler::property_t(value);
    })
    .def_static("from_long_vector", [](const std::vector<long>& value) {
        return ObjectHandler::property_t(value);
    })
    .def_static("from_double_vector", [](const std::vector<double>& value) {
        return ObjectHandler::property_t(value);
    })
    .def_static("from_string_vector",
        [](const std::vector<std::string>& value) {
            return ObjectHandler::property_t(value);
        })

    .def("missing", &ObjectHandler::property_t::missing);
    '''

    lines.extend([
        "",
        "namespace py = pybind11;",
        "",
        f"PYBIND11_MODULE({args.module}, m)",
        "{",
        cpp_code
    ])

    for function in functions:
        lines.append(
            generate_binding(function)
        )

    lines.extend([
        "}",
        "",
    ])

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_text(
        "\n".join(lines)
    )

    print(f"Found {len(functions)} functions")
    print(f"Generated: {output}")


if __name__ == "__main__":
    main()
