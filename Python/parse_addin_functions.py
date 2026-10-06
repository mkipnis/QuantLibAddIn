from pathlib import Path
import xml.etree.ElementTree as ET


FUNCTION_TAGS = {
    "Constructor",
    "Member",
    "Function",
}


def parse_function(element, xml_file):
    """
    Convert a Constructor/Member/Function XML element
    into a Python dictionary.
    """

    result = {
        "name": element.get("name"),
        "kind": element.tag,
        "type": element.get("type"),
        "library_function": element.findtext("libraryFunction"),
        "description": element.findtext("description"),
        "file": str(xml_file),
        "parameters": [],
    }

    parameters = element.find("ParameterList/Parameters")

    if parameters is not None:
        for parameter in parameters.findall("Parameter"):

            result["parameters"].append({
                "name": parameter.get("name"),
                "type": parameter.findtext("type"),
                "tensor_rank": parameter.findtext("tensorRank"),
                "default": parameter.get("default"),
                "const": parameter.get("const"),
                "description": parameter.findtext("description"),
                "example": parameter.get("exampleValue"),
            })

    return result


def load_xml_functions(directories):
    """
    Load XML function definitions from multiple directories.

    All *.xml files under the specified directories are searched
    recursively.

    Returns:
        dict:
            Dictionary indexed by the XML 'name' attribute.

    Example:

        functions["qlAbcdFunction"]

        functions["qlAbcdFunctionInstantaneousValue"]
    """

    functions = {}

    for directory in directories:

        directory = Path(directory)

        if not directory.exists():
            print(f"Warning: directory does not exist: {directory}")
            continue

        if not directory.is_dir():
            print(f"Warning: not a directory: {directory}")
            continue

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

                functions[name] = parse_function(
                    element,
                    xml_file
                )

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

    for parameter in function["parameters"]:

        print(
            f"  {parameter['name']}: "
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


def main():

    directories = [
        "/Users/mkipnis/git/QuantLibAddin/QuantLibAddin/Addins",
        "/Users/mkipnis/git/QuantLibAddin/QuantLibAddin",
    ]

    functions = load_xml_functions(directories)

    print(f"Loaded {len(functions)} functions")

    # ------------------------------------------------------------
    # Look up a function by name
    # ------------------------------------------------------------

    name = "qlAbcdFunction"

    if name in functions:
        print_function(functions[name])
    else:
        print(f"Function not found: {name}")

    # ------------------------------------------------------------
    # Another example
    # ------------------------------------------------------------

    name = "qlAbcdFunctionInstantaneousCovariance"

    if name in functions:
        print_function(functions[name])
    else:
        print(f"Function not found: {name}")


    # ------------------------------------------------------------
    # Another example
    # ------------------------------------------------------------

    name = "qlSchedule"

    if name in functions:
        print_function(functions[name])
    else:
        print(f"Function not found: {name}")


    name = "qlDiscountingSwapEngine"

    if name in functions:
        print_function(functions[name])
    else:
        print(f"Function not found: {name}")


if __name__ == "__main__":
    main()