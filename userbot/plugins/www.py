#
# PaperplaneRemix - A modular Telegram selfbot script
# Copyright (C) 2022, Avinash Reddy and the PaperplaneRemix contributors
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import asyncio
import concurrent
import functools
import sys
from typing import Tuple

from speedtest import Speedtest
import wikipedia

from telethon.tl import functions

from userbot import client
from userbot.utils.helpers import get_chat_link, format_speed
from userbot.utils.events import NewMessage

plugin_category = "www"

DCs = {
    1: "149.154.175.50",
    2: "149.154.167.51",
    3: "149.154.175.100",
    4: "149.154.167.91",
    5: "91.108.56.149",
}

testing = "`Testing from %(isp)s`"
hosted = "`Hosted by %(sponsor)s (%(name)s) [%(d)0.2f km]: %(latency)s ms`"
download = "`Download: %0.2f %s%s/s`"
upload = "`Upload: %0.2f %s%s/s`"


@client.onMessage(
    command=("nearestdc", plugin_category), outgoing=True, regex=r"nearestdc$"
)
async def nearestdc(event: NewMessage.Event) -> None:
    """
    Get information of your country and data center information.


    `{prefix}nearestdc`
    """
    result = await client(functions.help.GetNearestDcRequest())
    text = (
        f"**Country:** `{result.country}`\n"
        + f"**This DC:** `{result.this_dc}`\n"
        + f"**Nearest DC:** `{result.nearest_dc}`"
    )
    await event.answer(text)


@client.onMessage(
    command=("pingdc", plugin_category), outgoing=True, regex=r"pingdc(?: |$)(\d+)?"
)
async def pingdc(event: NewMessage.Event) -> None:
    """
    Ping your or other data center's IP addresses.


    `{prefix}pingdc` or **{prefix}pingdc (1|2|3|4|5)**
        This might not work if your connection blocks the requests
    """
    if event.matches[0].group(1) in ("1", "2", "3", "4", "5"):
        dc = int(event.matches[0].group(1))
    else:
        raw_dc = await client(functions.help.GetNearestDcRequest())
        dc = raw_dc.this_dc
    param = "-n" if sys.platform.startswith("win") else "-c"
    cmd = f"ping {param} 1 {DCs[dc]}"

    if sys.platform.startswith("win"):
        out, err = await _sub_shell(cmd)
        average = out.split("Average = ")[1]
    else:
        out, err = await _sub_shell(cmd + " | awk -F '/' 'END {print $5}'")
        average = out.strip() + "ms"

    if len(out.strip()) == 0:
        await event.answer("`Make sure your system's routing access isn't deprecated.`")
        return

    if err:
        await event.answer(err)
        return
    await event.answer(f"DC {dc}'s average response: `{average}`")


@client.onMessage(
    command=("speedtest", plugin_category),
    outgoing=True,
    regex=r"speedtest(?: |$)(bit|byte)?s?$",
)
async def speedtest(event: NewMessage.Event) -> None:
    """
    Perform a speedtest with the best available server based on ping.


    `{prefix}speedtest` of **{prefix}speedtest (bits|bytes)**
    """
    unit = ("bit", 1)
    arg = event.matches[0].group(1)
    if arg and arg.lower() == "byte":
        unit = ("byte", 8)

    s = Speedtest()
    speed_event = await event.answer(testing % s.results.client)
    await _run_sync(s.get_servers)

    await _run_sync(s.get_best_server)
    text = f"{speed_event.text}\n{hosted % s.results.server}"
    speed_event = await event.answer(text)

    await _run_sync(s.download)
    down, unit0, unit1 = await format_speed(s.results.download, unit)
    text = f"{speed_event.text}\n{download % (down, unit0, unit1)}"
    speed_event = await event.answer(text)

    await _run_sync(s.upload)
    up, unit0, unit1 = await format_speed(s.results.upload, unit)
    text = f"{speed_event.text}\n{upload % (up, unit0, unit1)}"
    extra = await get_chat_link(event, event.id)
    await event.answer(text, log=("speedtest", f"Performed a speedtest in {extra}."))


@client.onMessage(
    command=("wiki", plugin_category), outgoing=True, regex=r"(wk|wiki)(?: |$|\n)(.*)"
)
async def urban_dict(event: NewMessage.Event) -> None:
    """
    Searches Wikipedia for the given text.


    `{prefix}wiki Wikipedia`"""
    query = event.matches[0].group(2)
    try:
        result = await _run_sync(functools.partial(wikipedia.summary, query))
    except (
        wikipedia.exceptions.DisambiguationError,
        wikipedia.exceptions.PageError,
    ) as error:
        await event.answer(f"**Error:**\n`{error}`")
        return
    await event.answer(f"**Text:** `{query}`\n\n**Result:**\n__{result}__")


async def _sub_shell(cmd: str) -> Tuple[str, str]:
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    return stdout.decode("UTF-8"), stderr.decode("UTF-8")


async def _run_sync(func: callable):
    return await client.loop.run_in_executor(
        concurrent.futures.ThreadPoolExecutor(), func
    )
