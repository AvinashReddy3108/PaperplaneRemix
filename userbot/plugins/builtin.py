#
# PaperplaneRemix - A modular Telegram selfbot script
# Copyright (C) 2022, Avinash Reddy and the PaperplaneRemix contributors
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import datetime
import io
import logging
import os
import sys

from userbot import LOGGER, client, loggingHandler
from userbot.utils.events import NewMessage
from userbot.utils.helpers import restart


@client.onMessage(command=("ping", "www"), outgoing=True, regex=r"ping$", builtin=True)
async def ping(event: NewMessage.Event) -> None:
    """
    Check how long it takes to get an update and respond to it.


    `{prefix}ping`
    """
    start = datetime.datetime.now()
    await event.answer("**PONG**")
    duration = datetime.datetime.now() - start
    milliseconds = duration.microseconds / 1000
    await event.answer(f"**PONG:** `{milliseconds}ms`")


@client.onMessage(
    command=("shutdown", "misc"), outgoing=True, regex=r"shutdown$", builtin=True
)
async def shutdown(event: NewMessage.Event) -> None:
    """
    Shutdown the userbot script.


    `{prefix}shutdown`
    """
    await event.answer("`Disconnecting the client and exiting. Ciao!`")
    client.reconnect = False
    LOGGER.info("Disconnecting the client and exiting the main script.")
    await client.disconnect()


@client.onMessage(
    command=("restart", "misc"), outgoing=True, regex=r"restart$", builtin=True
)
async def restarter(event: NewMessage.Event) -> None:
    """
    Restart the userbot script.


    `{prefix}restart`
    """
    await event.answer(
        "`BRB disconnecting and starting the script again!`",
        log=("restart", "Restarted the userbot script"),
    )
    await restart(event)


@client.onMessage(
    command=("loglevel", "logging"),
    outgoing=True,
    regex=r"loglevel(?: |$)(\w*)",
    builtin=True,
)
async def flushLevelChanger(event: NewMessage.Event) -> None:
    """
    Change or get the default console logger level


    **{prefix}loglevel** or **{prefix}loglevel (level)**
        **Example:** `{prefix}loglevel` or `{prefix}loglevel info`
    """
    match = event.matches[0].group(1)
    if not match:
        level = logging._levelToName.get(loggingHandler.flushLevel, "N/A")
        await event.answer(f"`Current console logging level is set to: {level}`")
        return
    if match.isdigit():
        level = int(match)
        if (level % 10 != 0) or (level > 50) or (level < 0):
            await event.answer("**Invalid log level specified!**")
            return
    else:
        level = logging._nameToLevel.get(match.upper(), None)
        if not level:
            await event.answer("**Invalid log level specified!**")
            return
    loggingHandler.setFlushLevel(level)
    _level = logging._levelToName.get(level, "INFO")
    client.config["userbot"]["console_logger_level"] = _level
    client._updateconfig()
    await event.answer(
        f"`Successfully changed the logging level to: {_level}`",
        log=("logging", f"Changed the console log level tp {_level}"),
    )


@client.onMessage(
    command=("logs", "logging"),
    outgoing=True,
    regex=r"logs(?: |$)(\d+|\w+)?",
    builtin=True,
)
async def logsDump(event: NewMessage.Event) -> None:
    """
    Get a text file of all the logs pending in the memory buffer


    **{prefix}logs** or **{prefix}logs (info/debug/error)**
        **Example:** `{prefix}logs` or `{prefix}logs info`
    """
    match = event.matches[0].group(1)
    level = None
    if match:
        if match.isdigit():
            level = int(match)
            if (level % 10 != 0) or (level > 50) or (level < 0):
                await event.answer("**Invalid log level specified!**")
                return
        else:
            level = logging._nameToLevel.get(match.upper(), None)
            if not level:
                await event.answer("**Invalid log level specified!**")
                return
    if dump := loggingHandler.dumps(level):
        output = io.BytesIO("\n".join(dump).encode())
        output.name = "logs.txt"
        await event.answer(file=output)
    else:
        await event.answer("`No logs found`")


@client.onMessage(
    command=("clearlogs", "logging"),
    outgoing=True,
    regex=r"(clear|flush) logs$",
    builtin=True,
)
async def flushStdOut(event: NewMessage.Event) -> None:
    """
    Flush the logged buffers and clear the standard output


    `{prefix}clear logs` or `{prefix}flush logs`
    """
    loggingHandler.flushBuffers()
    if sys.platform.startswith("win"):
        os.system("cls")
    else:
        os.system("clear")
    await event.answer("`Successfully flushed all the logs`")
