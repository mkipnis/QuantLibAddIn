# Copyright (c) Mike Kipnis

import tree_sitter_cpp as tscpp
from tree_sitter import Language, Parser
import json

from helpers.type_converter import is_property_type, convert_type
from parsers.parse_addin_functions import print_function

CPP_LANGUAGE = Language(tscpp.language())

def make_parser():
    """Support current and older py-tree-sitter APIs."""
    try:
        return Parser(CPP_LANGUAGE)
    except TypeError:
        parser = Parser()
        parser.language = CPP_LANGUAGE
        return parser

def text_of(source, node):
    return source[node.start_byte:node.end_byte].decode("utf-8")

def descendants(node, kind):
    """Yield descendants of a particular syntax-node type."""
    for child in node.children:
        if child.type == kind:
            yield child
        yield from descendants(child, kind)

def find_namespaces(node, source, parents=None):
    """Find function declarations and their enclosing namespaces."""
    if parents is None:
        parents = []

    if node.type == "namespace_definition":
        name_node = node.child_by_field_name("name")
        body_node = node.child_by_field_name("body")

        if body_node:
            name = text_of(source, name_node) if name_node else ""
            yield from find_namespaces(
                body_node,
                source,
                parents + ([name] if name else []),
            )
        return

    if node.type == "function_definition":
        return

    if node.type == "declaration":
        for child in node.children:
            if child.type == "function_declarator":
                yield parents, child, node
                break

    for child in node.children:
        yield from find_namespaces(child, source, parents)


def function_name_and_params(declarator, source):
    """Extract a function name and parameter declarations."""
    name_node = declarator.child_by_field_name("declarator")
    params_node = declarator.child_by_field_name("parameters")

    if name_node is None:
        return None, []

    # The declarator may wrap the identifier in a qualified identifier.
    while name_node and name_node.type not in (
        "identifier",
        "field_identifier",
        "qualified_identifier",
        "operator_name",
    ):
        nested = name_node.child_by_field_name("declarator")
        if nested is None:
            break
        name_node = nested

    if name_node is None:
        return None, []

    name = text_of(source, name_node).split("::")[-1]

    params = []

    if params_node:
        for child in params_node.named_children:
            if child.type in ("parameter_declaration", "optional_parameter_declaration"):
                params.append(child)

    return name, params


def parameter_info(param, source):
    """Return a parameter's name and declared C++ type."""
    declarator = param.child_by_field_name("declarator")
    type_node = param.child_by_field_name("type")

    name = None

    if declarator:
        # Find an identifier inside reference/pointer/array declarators.
        for candidate in descendants_including_self(declarator):
            if candidate.type in ("identifier", "field_identifier"):
                name = text_of(source, candidate)
                break

    type_text = text_of(source, type_node) if type_node else ""

    if declarator:
        # Preserve const, &, *, and pointer/reference syntax.
        declarator_text = text_of(source, declarator)
        if name:
            type_text = (
                type_text + " " +
                declarator_text.replace(name, "").strip()
            ).strip()

    return name, type_text


def descendants_including_self(node):
    yield node
    for child in node.children:
        yield from descendants_including_self(child)



def generate_binding( namespace, declarator, source, ql_addin_function_defs):
    name, params = function_name_and_params(declarator, source)

    if not name:
        return None

    qualified_name = "::".join(namespace + [name])

    py_args = []

    # Look up the function definition and its parameter metadata.
    qladdin_function_def = ql_addin_function_defs.get(name, None)

    if qladdin_function_def is None:
        return None

    print_function(qladdin_function_def)

    qladdin_function_def_params = qladdin_function_def.get("parameters", {})

    for index, param in enumerate(params):
        param_name, type_name = parameter_info(param, source)

        # Each parameter's XML metadata is keyed by parameter name.
        quantlib_addin_param = qladdin_function_def_params.get(param_name, {})
        description = quantlib_addin_param.get("description") or ""

        param_details = convert_type(param_name, type_name, quantlib_addin_param)

        param_details["param_name"] = param_name
        param_details["description"] = description
        param_details["argument"] = f'py::arg("{param_name}")'

        py_args.append(param_details)

    # Build a docstring containing the function and parameter descriptions.
    doc_lines = []

    function_description = (
        qladdin_function_def.get("description") or ""
    ).strip()

    if function_description:
        doc_lines.append(function_description)

    if doc_lines and any(arg["description"].strip() for arg in py_args):
        doc_lines.append("")

    for arg in py_args:
        description = arg["description"].strip()

        if description:
            doc_lines.append(
                f"{arg['param_name']}: {description}"
            )

    docstring = "\n".join(doc_lines)

    # Generate the pybind11 binding.
    lines = [
        f'm.def("{name}",',
        "",
        "    [](",
        ",\n".join(
            f"        {arg['lambda_param']}" for arg in py_args
        ),
        "    )",
        "    {",
        f"        return {qualified_name}(",
        ",\n".join(
            f"            {arg['call_param']}" for arg in py_args
        ),
        "        );",
        "    }",
    ]

    # Add py::arg(...) entries only when arguments exist.
    if py_args:
        lines[-1] += ","
        lines.append(
            ",\n".join(
                f"    {arg['argument']}" for arg in py_args
            )
        )

    # Add the docstring as an argument to m.def(), if available.
    if docstring:
        lines[-1] += ","
        lines.append(f"    {json.dumps(docstring)}")

    # Close m.def() exactly once.
    lines.append(");")

    return "\n".join(lines)