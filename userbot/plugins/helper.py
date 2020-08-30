# TG-UserBot - A modular Telegram UserBot script for Python.
# Copyright (C) 2019 Kandarp <https://github.com/kandnub>
#
# TG-UserBot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TG-UserBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TG-UserBot.  If not, see <https://www.gnu.org/licenses/>.

import os.path
import re
from typing import Tuple

from userbot import client
from userbot.utils.events import NewMessage

plugin_category: str = "helper"
link: str = "https://github.com/AvinashReddy3108/PaperplaneRemix/wiki"
chunk: int = 5
split_exp: re.Pattern = re.compile(r"\||\/")


@client.onMessage(
    command=("setprefix", plugin_category),
    outgoing=True,
    regex=r"setprefix (.+)",
    builtin=True,
)
async def setprefix(event: NewMessage.Event) -> None:
    """
    Change the bot's default prefix.


    {prefix}setprefix (new prefix)**
        **Example:** `{prefix}setprefix ;`
    """
    match = event.matches[0].group(1).strip()
    old_prefix = client.prefix
    client.prefix = match
    client.config["userbot"]["userbot_prefix"] = match
    if old_prefix is None:
        await event.answer(
            "`Successfully changed the prefix to `**{0}**`. "
            "To revert this, do `**resetprefix**".format(client.prefix),
            log=("setprefix", f"Prefix changed to {client.prefix}"),
        )
    else:
        await event.answer(
            "`Successfully changed the prefix to `**{0}**`. "
            "To revert this, do `**{0}setprefix {1}**".format(
                client.prefix, old_prefix
            ),
            log=("setprefix", f"prefix changed to {client.prefix} from {old_prefix}"),
        )
    client._updateconfig()


@client.onMessage(
    command=("resetprefix", plugin_category),
    outgoing=True,
    regex=r"(?i)^resetprefix$",
    disable_prefix=True,
    builtin=True,
)
async def resetprefix(event: NewMessage.Event) -> None:
    """
    Reset the bot's prefix to the default ones.


    `resetprefix`
    """
    prefix = client.config["userbot"].get("userbot_prefix", None)
    if prefix:
        del client.config["userbot"]["userbot_prefix"]
        client.prefix = None
        await event.answer(
            "`Successfully reset your prefix to the deafult ones!`",
            log=("resetprefix", "Successfully reset your prefix"),
        )
        client._updateconfig()
    else:
        await event.answer("`There is no prefix set as a default!`")


@client.onMessage(
    command=("enable", plugin_category),
    outgoing=True,
    regex=r"enable(?: |$)(\w+)?$",
    builtin=True,
)
async def enable(event: NewMessage.Event) -> None:
    """
    Enable a command IF it's already disabled.


    **{prefix}enable (command)**
        **Example:** `{prefix}enable afk`
    """
    arg = event.matches[0].group(1)
    if not arg:
        await event.answer("`Enable what? The void?`")
        return
    commands, command_list = await solve_commands(client.disabled_commands)
    command = commands.get(arg, command_list.get(arg, False))
    if command:
        for handler in command.handlers:
            client.add_event_handler(command.func, handler)
        enabled_coms = ", ".join(split_exp.split(arg)) if arg in command_list else arg
        client.commands[arg] = command
        client.disabled_commands.pop(arg)
        await event.answer(
            f"`Successfully enabled {enabled_coms}`",
            log=("enable", f"Enabled command(s): {enabled_coms}"),
        )
    else:
        await event.answer(
            "`Couldn't find the specified command. " "Perhaps it's not disabled?`"
        )


@client.onMessage(
    command=("disable", plugin_category),
    outgoing=True,
    regex=r"disable(?: |$)(\w+)?$",
    builtin=True,
)
async def disable(event: NewMessage.Event) -> None:
    """
    Disable a command IF it's already enabled.


    **{prefix}disable (command)**
        **Example:** `{prefix}disable afk`
    """
    arg = event.matches[0].group(1)
    if not arg:
        await event.answer("`Disable what? The void?`")
        return
    commands, command_list = await solve_commands(client.commands)
    command = commands.get(arg, command_list.get(arg, False))
    if command:
        if command.builtin:
            await event.answer("`Cannot disable a builtin command.`")
        else:
            client.remove_event_handler(command.func)
            disabled_coms = (
                ", ".join(split_exp.split(arg)) if arg in command_list else arg
            )
            client.disabled_commands[arg] = command
            client.commands.pop(arg)
            await event.answer(
                f"`Successfully disabled {disabled_coms}`",
                log=("disable", f"Disabled command(s): {disabled_coms}"),
            )
    else:
        await event.answer("`Couldn't find the specified command.`")


@client.onMessage(
    command=("enabled", plugin_category), outgoing=True, regex=r"enabled$", builtin=True
)
async def commands(event: NewMessage.Event) -> None:
    """
    A list of all the currently enabled commands.


    `{prefix}enabled`
    """
    response = "**Enabled commands:**"
    commands, _ = await solve_commands(client.commands)
    enabled = sorted(commands.keys())
    for i in range(0, len(enabled), chunk):
        response += "\n  "
        response += ",\t\t".join("`" + c + "`" for c in enabled[i : i + chunk])
    await event.answer(response)


@client.onMessage(
    command=("disabled", plugin_category),
    outgoing=True,
    regex=r"disabled$",
    builtin=True,
)
async def disabled(event: NewMessage.Event) -> None:
    """
    A list of all the currently disabled commands.


    `{prefix}disabled`
    """
    disabled_commands, _ = await solve_commands(client.disabled_commands)

    if not disabled_commands:
        await event.answer("`There are no disabled commands currently.`")
        return

    response = "**Disabled commands:**"
    disabled = sorted(disabled_commands.keys())
    for i in range(0, len(disabled), chunk):
        response += "\n  "
        response += ",\t\t".join("`" + c + "`" for c in disabled[i : i + chunk])
    await event.answer(response)


@client.onMessage(
    command=("help", plugin_category),
    builtin=True,
    outgoing=True,
    regex=r"help(?: |$)(\w*)(?: |$)(dev|details|info)?",
)
async def helper(event: NewMessage.Event) -> None:
    """
    A list of commands categories, their commands or command's details.


    **{prefix}help (all|category|command) [dev|details|info]**
        **Example:** `{prefix}help afk` or `{prefix}help afk dev`
    """
    arg = event.matches[0].group(1)
    arg1 = event.matches[0].group(2)
    enabled, senabled = await solve_commands(client.commands)
    disabled, sdisabled = await solve_commands(client.disabled_commands)
    categories = client.commandcategories
    prefix = client.prefix or "."
    if arg:
        arg = arg.lower()
        if arg in (*enabled, *disabled, *senabled, *sdisabled):
            command = None
            for i in (enabled, disabled, senabled, sdisabled):
                if arg in i:
                    command = i.get(arg)
                    break
            text = (
                f"**Here's the info for the** `{arg}` **command:**\n\n"
                f"• **Can be disabled:** `{'Yes' if not command.builtin else 'No'}`\n"
            )
            if arg1:
                filename = command.func.__code__.co_filename
                if not filename.startswith("http"):
                    filename = f"`{os.path.relpath(filename)}`"
                text += (
                    "\n• **Dev/Debug Info:**\n"
                    f"   - **File:** {filename}\n"
                    f"      - **Registered function:** `{command.func.__name__}`\n"
                    f"      - **Line:** `{command.func.__code__.co_firstlineno}`\n"
                )
            text += (
                "\n• **Info:**\n"
                f"{command.info}\n"
                "\n• **Syntax:**\n"
                f"{command.usage.format(prefix=prefix)}"
            )
        elif arg in categories:
            category = categories.get(arg)
            text = f"**{arg.title()} commands:**"
            for com in sorted(category):
                text += f"\n    • **{' | '.join(split_exp.split(com))}**"
        else:
            await event.answer("`Couldn't find the specified command or category!`")
            return
    else:
        text = (
            f"Documented commands can be found [HERE!]({link})\n"
            f"**Usage:**\n"
            f"  __{client.prefix or '.'}help <category>__\n"
            f"  __{client.prefix or '.'}help <command>__\n\n"
            "**Available command categories:**"
        )
        for category in sorted(categories.keys()):
            text += f"\n    • **{category}**"
    await event.answer(text, link_preview=False)


async def solve_commands(commands: dict) -> Tuple[dict, dict]:
    new_dict: dict = {}
    com_tuples: dict = {}
    for com_names, command in commands.items():
        splat = split_exp.split(com_names)
        if splat:
            for n in splat:
                com_tuples[n] = command
                new_dict[" | ".join(splat)] = command
        else:
            new_dict[com_names] = command
    return new_dict, com_tuples
