#!/usr/bin/env python3

import argparse
import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Type / function replacements
# ---------------------------------------------------------------------------

REPLACEMENTS = {
    # Smart pointers
    r"\bboost::shared_ptr\b": "std::shared_ptr",
    r"\bboost::weak_ptr\b": "std::weak_ptr",
    r"\bboost::scoped_ptr\b": "std::unique_ptr",

    # Smart pointer creation
    r"\bboost::make_shared\b": "std::make_shared",

    # Shared pointer casts
    r"\bboost::dynamic_pointer_cast\b": "std::dynamic_pointer_cast",
    r"\bboost::static_pointer_cast\b": "std::static_pointer_cast",
    r"\bboost::const_pointer_cast\b": "std::const_pointer_cast",

    # shared_from_this
    r"\bboost::enable_shared_from_this\b":
        "std::enable_shared_from_this",

    r"\bboost::shared_from_this\b":
        "std::shared_from_this",
}


# ---------------------------------------------------------------------------
# Boost headers that can be replaced by <memory>
# ---------------------------------------------------------------------------

BOOST_MEMORY_HEADERS = {
    "boost/shared_ptr.hpp",
    "boost/weak_ptr.hpp",
    "boost/scoped_ptr.hpp",
    "boost/make_shared.hpp",
    "boost/enable_shared_from_this.hpp",
    "boost/smart_ptr.hpp",
}


HEADER_PATTERN = re.compile(
    r'^[ \t]*#include[ \t]*[<"]([^>"]+)[>"][ \t]*$',
    re.MULTILINE,
)


def replace_headers(text: str) -> str:
    """
    Replace Boost smart-pointer headers with <memory>.

    If multiple Boost smart-pointer headers are present, they are all removed
    and a single #include <memory> is inserted where the first one occurred.
    """

    memory_needed = False
    first_header_start = None
    first_header_end = None

    matches = list(HEADER_PATTERN.finditer(text))

    for match in matches:
        header = match.group(1)

        if header not in BOOST_MEMORY_HEADERS:
            continue

        memory_needed = True

        if first_header_start is None:
            first_header_start = match.start()
            first_header_end = match.end()

    if not memory_needed:
        return text

    # Remove all Boost smart-pointer includes.
    result = HEADER_PATTERN.sub(
        lambda match: ""
        if match.group(1) in BOOST_MEMORY_HEADERS
        else match.group(0),
        text,
    )

    # Add <memory> if it isn't already present.
    if not re.search(
        r'^[ \t]*#include[ \t]*<memory>[ \t]*$',
        result,
        re.MULTILINE,
    ):
        # Insert <memory> near the beginning of the include section.
        include_match = re.search(
            r'^[ \t]*#include\b.*$',
            result,
            re.MULTILINE,
        )

        if include_match:
            position = include_match.start()
            result = (
                result[:position]
                + "#include <memory>\n"
                + result[position:]
            )
        else:
            result = "#include <memory>\n\n" + result

    # Clean up excessive blank lines created by removed headers.
    result = re.sub(r'\n{3,}', '\n\n', result)

    return result


def replace_boost_types(text: str) -> str:
    for pattern, replacement in REPLACEMENTS.items():
        text = re.sub(pattern, replacement, text)

    return text


def process_file(path: Path) -> bool:
    try:
        original = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"Skipping non-UTF-8 file: {path}")
        return False

    updated = original

    # Replace Boost smart-pointer headers.
    updated = replace_headers(updated)

    # Replace Boost smart-pointer types/functions.
    updated = replace_boost_types(updated)

    if updated == original:
        return False

    path.write_text(updated, encoding="utf-8")
    print(f"Updated: {path}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Replace Boost smart pointers with std smart pointers "
            "in C/C++ source files."
        )
    )

    parser.add_argument(
        "directory",
        type=Path,
        help="Directory to process recursively",
    )

    args = parser.parse_args()

    if not args.directory.is_dir():
        raise SystemExit(f"Not a directory: {args.directory}")

    extensions = {".cpp", ".hpp", ".h"}

    files_processed = 0
    files_changed = 0

    for path in args.directory.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() not in extensions:
            continue

        files_processed += 1

        if process_file(path):
            files_changed += 1

    print()
    print(f"Files processed: {files_processed}")
    print(f"Files changed:   {files_changed}")


if __name__ == "__main__":
    main()
