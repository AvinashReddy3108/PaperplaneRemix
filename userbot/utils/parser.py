#
# PaperplaneRemix - A modular Telegram selfbot script
# Copyright (C) 2022, Avinash Reddy and the PaperplaneRemix contributors
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

# This is based on the parser of https://github.com/mojurasu/kantek/

import re
from typing import Union

KWARGS = re.compile(
    r"(?<!\S)"  # Make sure the key starts after a whitespace
    r"(?:(?P<q>\'|\")?)(?P<key>(?(q).+?|(?!\d)\w+?))(?(q)(?P=q))"
    r"(?::(?!//)|=)\s?"
    r"(?P<val>\[.+?\]|(?P<q1>\'|\").+?(?P=q1)|\S+)"
)
ARGS = re.compile(r"(?:(?P<q>\'|\"))(.+?)(?:(?P=q))")
BOOL_MAP = {
    "false": False,
    "true": True,
}

Value = Union[int, str, float, list]
KeywordArgument = Union[Value, range, list[Value]]


async def _parse_arg(val: str) -> Union[int, str, float]:
    val = val.strip()

    if re.match(r"^-?\d+$", val):
        return int(val)

    try:
        return float(val)
    except ValueError:
        pass

    if isinstance(val, str):
        if re.search(r"^\[.*\]$", val):
            val = re.sub(r"[\[\]]", "", val).split(",")
            val = [await _parse_arg(v.strip()) for v in val]
        else:
            val = BOOL_MAP.get(val.lower(), val)
    if isinstance(val, str):
        val = re.sub(r"(?<!\\), ?$", "", val)
    return val


@staticmethod
async def parse_arguments(
    arguments: str,
) -> tuple[list[Value], dict[str, KeywordArgument]]:
    keyword_args = {}
    for match in KWARGS.finditer(arguments):
        key = match.group("key")
        val = await _parse_arg(re.sub(r"[\'\"]", "", match.group("val")))
        keyword_args.update({key: val})
    arguments = KWARGS.sub("", arguments)

    args = [await _parse_arg(val.group(2)) for val in ARGS.finditer(arguments)]

    arguments = ARGS.sub("", arguments)

    for val in re.findall(r"([^\r\n\t\f\v ,]+|\[.*\])", arguments):
        parsed = await _parse_arg(val)
        if parsed:
            args.append(parsed)
    return args, keyword_args
