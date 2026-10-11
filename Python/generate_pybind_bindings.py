# Copyright (c) Mike Kipnis

import argparse
from pathlib import Path

from helpers.pybind_writer import write_pybind_file
from parsers.header_parser import make_parser, find_namespaces, generate_binding
from parsers.parse_addin_functions import load_xml_functions

def main():

    cli = argparse.ArgumentParser(description="Generate pybind11 bindings from QuantLibAddinCpp")

    cli.add_argument("directory", help="Root directory containing .hpp files")
    cli.add_argument("output", help="Output C++ file")

    cli.add_argument("--object-handler-function-dir", help="Object Handler Function Directory - ObjectHandler/gensrc/metadata/functions")
    cli.add_argument("--quantlib-addin-function-dir", help="QuantLibAddin Function Directory - QuantLibAddin/gensrc/metadata/functions")

    cli.add_argument("--namespace", default="QuantLibAddinCpp")
    cli.add_argument("--module", default="quantlib_addin")

    args = cli.parse_args()

    root = Path(args.directory).resolve()
    output = Path(args.output).resolve()
    target_namespace = args.namespace.split("::")

    object_handler_dir = Path(args.object_handler_function_dir).resolve()
    quantlib_addin_dir = Path(args.quantlib_addin_function_dir).resolve()

    functions = load_xml_functions(object_handler_dir)
    functions.update(load_xml_functions(quantlib_addin_dir))

    parser = make_parser()
    bindings = []
    headers = sorted(root.rglob("*.hpp"))

    if not headers:
        raise SystemExit(f"No .hpp files found in {root}")

    for header in headers:
        source = header.read_bytes()
        tree = parser.parse(source)

        for namespace, declarator, declaration in find_namespaces(tree.root_node, source):
            if namespace != target_namespace:
                continue

            binding = generate_binding(namespace, declarator, source, functions)

            if binding:
                bindings.append(binding)

    write_pybind_file(headers, args.module, bindings, output)

    print(f"Found {len(bindings)} functions")
    print(f"Generated: {output}")


if __name__ == "__main__":
    main()