# Copyright (c) Mike Kipnis

CONVERSION_HELPERS = r"""
template <typename T>
ObjectHandler::property_t property_from(const py::object& value)
{
    return ObjectHandler::property_t(value.cast<T>());
}

ObjectHandler::property_t property_from_date(const py::object& value)
{
    if (value.is_none())
        return {};

    const QuantLib::Date date = py::isinstance<py::int_>(value)
        ? QuantLib::Date(value.cast<QuantLib::Date::serial_type>())
        : value.cast<QuantLib::Date>();

    return ObjectHandler::property_t(
        static_cast<long>(date.serialNumber())
    );
}

"""
