# Copyright (c) Mike Kipnis

import re

def is_property_type(type_text):
    normalized = re.sub(r"\b(const|volatile)\b|[&*]", "", type_text)
    normalized = re.sub(r"\s+", "", normalized)

    return normalized in (
        "ObjectHandler::property_t",
        "::ObjectHandler::property_t",
    )

def convert_type(param_name, type_name, ql_addin_type):
    if is_property_type(type_name):
        quantlib_type = ql_addin_type.get("type", "")

        if not quantlib_type and param_name in {"Trigger", "Permanent"}:
            quantlib_type = "bool"

        type_mapping = {
            "QuantLib::Date": "date",
            "QuantLib::Size": "long",
            "QuantLib::Quote": "double",
            "QuantLib::Real": "double",
        }

        quantlib_type = type_mapping.get(quantlib_type, quantlib_type)

        if quantlib_type not in {
            "string", "bool", "int", "long", "double", "date"
        }:
            quantlib_type = "string"

        if quantlib_type == "date":
            call_param = f"property_from_date({param_name})"
        else:
            cpp_type_mapping = {
                "string": "std::string",
                "bool": "bool",
                "int": "int",
                "long": "long",
                "double": "double",
            }
            cpp_type = cpp_type_mapping[quantlib_type]
            call_param = f"property_from<{cpp_type}>({param_name})"

        param_details = {
            "lambda_param": f"py::object {param_name}",
            "call_param": call_param,
        }
    else:
        param_details = {
            "lambda_param": f"{type_name} {param_name}",
            "call_param": param_name,
        }

    return param_details
