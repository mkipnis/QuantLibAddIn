# Copyright (c) Mike Kipnis
from pathlib import Path
import xml.etree.ElementTree as ET

FUNCTION_TAGS = {"Constructor", "Member", "Function", "Procedure"}

def parse_function(element, xml_file):
    result = {
        "name": element.get("name"),
        "kind": element.tag,
        "type": element.get("type"),
        "library_function": element.findtext("libraryFunction"),
        "description": element.findtext("description"),
        "file": str(xml_file),
        "parameters": {},
    }

    parameters = element.find("ParameterList/Parameters")

    if parameters is not None:
        for parameter in parameters.findall("Parameter"):
            name = parameter.get("name")

            if not name:
                continue

            result["parameters"][name] = {
                "name": name,
                "type": parameter.findtext("type"),
                "tensor_rank": parameter.findtext("tensorRank"),
                "default": parameter.get("default"),
                "const": parameter.get("const"),
                "description": parameter.findtext("description"),
                "example": parameter.get("exampleValue"),
            }

    return result


def load_xml_functions(quantlib_addin_cpp_dir):
    functions = {}
    directory = Path(quantlib_addin_cpp_dir)

    if not directory.is_dir():
        print(f"Warning: not a directory: {directory}")
        return functions

    for xml_file in directory.rglob("*.xml"):
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

        except ET.ParseError as e:
            print(f"Skipping invalid XML: {xml_file}")
            print(f"  {e}")
            continue

        for element in root.iter():
            if element.tag not in FUNCTION_TAGS:
                continue

            name = element.get("name")

            if not name:
                continue

            functions[name] = parse_function(element, xml_file)

    return functions

def print_function(function):
    """
    Pretty-print a parsed function definition.
    """

    print()
    print("=" * 70)

    print(f"Name:             {function['name']}")
    print(f"Kind:             {function['kind']}")
    print(f"Library function: {function['library_function']}")
    print(f"Type:             {function['type']}")
    print(f"File:             {function['file']}")

    if function["description"]:
        print(f"Description:      {function['description']}")

    print()
    print("Parameters:")

    for parameter in function["parameters"].values():

        print(
            f" {parameter['name']}: "
            f"{parameter['type']} "
            f"({parameter['tensor_rank']})"
        )

        if parameter["default"] is not None:
            print(f"      default: {parameter['default']}")

        if parameter["example"] is not None:
            print(f"      example: {parameter['example']}")

        if parameter["description"]:
            print(f"      {parameter['description']}")

    print("=" * 70)