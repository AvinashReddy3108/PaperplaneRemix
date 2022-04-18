#
# PaperplaneRemix - A modular Telegram selfbot script
# Copyright (C) 2022, Avinash Reddy and the PaperplaneRemix contributors
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import re
from typing import Tuple, Union

regexp = re.compile(r"(\d+)(w|d|h|m|s)?")
adminregexp = re.compile(r"\d+(?:w|d|h|m|s)?")


async def amount_to_secs(amount: tuple) -> int:
    """Resolves one unit to total seconds.

    Args:
        amount (``int``, ``str``):
            Tuple where str is the unit.

    Returns:
        ``int``:
            Total seconds of the unit on success.

    Example:
        >>> await amount_to_secs(("1", "m"))
        60

    """
    num, unit = amount

    num = int(num)
    if not unit:
        unit = "s"

    if unit == "d":
        return num * 60 * 60 * 24
    elif unit == "h":
        return num * 60 * 60
    elif unit == "m":
        return num * 60
    elif unit == "s":
        return num
    elif unit == "w":
        return num * 60 * 60 * 24 * 7
    else:
        return 0


async def string_to_secs(string: str) -> int:
    """Converts a time string to total seconds.

    Args:
        string (``str``):
            String conatining the time.

    Returns:
        ``int``:
            Total seconds of all the units.

    Example:
        >>> await string_to_sec("6h20m")
        22800

    """
    values = regexp.findall(string)

    totalValues = len(values)

    if totalValues == 1:
        return await amount_to_secs(values[0])
    return sum(await amount_to_secs(amount) for amount in values)


async def split_extra_string(string: str) -> Tuple[Union[str, None], Union[int, None]]:
    reason = string
    time = adminregexp.findall(string)
    for u in time:
        reason = reason.replace(u, "").strip()

    total_time = await string_to_secs("".join(time))

    return reason or None, total_time or None
