#
# PaperplaneRemix - A modular Telegram selfbot script
# Copyright (C) 2022, Avinash Reddy and the PaperplaneRemix contributors
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import asyncio
import inspect

from meval import meval

from userbot import client
from userbot.utils.events import NewMessage
from userbot.utils.helpers import get_chat_link

plugin_category = "scripting"


@client.onMessage(
    command=("eval", plugin_category), outgoing=True, regex=r"eval(?: |$|\n)([\s\S]*)"
)
async def evaluate(event: NewMessage.Event) -> None:
    """
    Evaluate Python expressions in the running script.


    **{prefix}eval (expression)**
        **Example:** `{prefix}eval 1+1`
    """
    expression = event.matches[0].group(1).strip()
    reply = await event.get_reply_message()
    if not expression:
        await event.answer("`Evaluated the void.`")
        return

    try:
        result = await meval(
            expression, globals(), client=client, event=event, reply=reply
        )
    except Exception as e:
        await event.answer(f"```{await client.get_traceback(e)}```", reply=True)
        return

    extra = await get_chat_link(event, event.id)
    if result and hasattr(result, "stringify"):
        if inspect.isawaitable(result):
            result = await result.stringify()
        else:
            result = result.stringify()
    result = str(result) if result else "Success?"
    await event.answer(
        "```" + result + "```",
        log=("eval", f"Successfully evaluated {expression} in {extra}!"),
        reply=True,
    )


@client.onMessage(
    command=("exec", plugin_category), outgoing=True, regex=r"exec(?: |$|\n)([\s\S]*)"
)
async def execute(event: NewMessage.Event) -> None:
    """
    Execute Python statements in a subprocess.


    **{prefix}exec (statement)**
        **Example:** `{prefix}exec import os; os.system('clear')`
    """
    statement = event.matches[0].group(1).strip()
    reply = await event.get_reply_message()
    if not statement:
        await event.answer("`Executed the void.`")
        return

    try:
        await meval(statement, globals(), client=client, event=event, reply=reply)
    except Exception as e:
        await event.answer(f"```{await client.get_traceback(e)}```", reply=True)
        return

    extra = await get_chat_link(event, event.id)
    await event.answer(
        "`Success?`",
        log=("exec", f"Successfully executed {statement} in {extra}!"),
        reply=True,
    )


@client.onMessage(
    command=("term", plugin_category), outgoing=True, regex=r"term(?: |$|\n)([\s\S]*)"
)
async def terminal(event: NewMessage.Event) -> None:
    """
    Execute terminal commands in a subprocess.


    **{prefix}term (command)**
        **Example:** `{prefix}term echo 123`
    """
    message = str(event.chat_id) + ":" + str(event.message.id)
    if client.running_processes.get(message, False):
        await event.answer("A process for this event is already running!", reply=True)
        return

    cmd = event.matches[0].group(1).strip()
    if not cmd:
        await event.answer("`Executed the void.`")
        return

    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    client.running_processes.update({message: process})
    stdout, stderr = await process.communicate()

    not_killed = client.running_processes.get(message, False)
    if not_killed:
        del client.running_processes[message]

    text = f"[TERM] Return code: {process.returncode}\n"

    if stdout:
        text += "\n[stdout]\n" + stdout.decode("UTF-8").strip() + "\n"
    if stderr:
        text += "\n[stderr]\n" + stderr.decode("UTF-8").strip() + "\n"

    extra = await get_chat_link(event, event.id)
    if stdout or stderr:
        await event.answer(
            "```" + text + "```",
            log=("term", f"Successfully executed {cmd} in {extra}!"),
            reply=True,
        )
    else:
        await event.answer("`Nice, get off the void.\nNo output for you!`")


@client.onMessage(
    command=("kill/terminate", plugin_category),
    outgoing=True,
    regex=r"(kill|terminate)$",
)
async def killandterminate(event: NewMessage.Event) -> None:
    """
    Kill or terminate a running subprocess by replying to the message.


    `{prefix}kill` or `{prefix}terminate`
    """
    if not event.reply_to_msg_id:
        await event.answer("`Reply to a message to kill or terminate the process!`")
        return

    reply = await event.get_reply_message()
    message = str(reply.chat_id) + ":" + str(reply.id)
    running_process = client.running_processes.get(message, False)

    if running_process:
        # If we ever want to wait for it to complete. (Most likely never)
        """try:
            await running_process.wait()
        finally:
            if running_process.returncode is None:"""

        option = event.matches[0].group(1)
        if option == "kill":
            running_process.kill()
        else:
            running_process.terminate()
        extra = await get_chat_link(event, reply.id)
        await event.answer(
            f"`Successfully {option}ed the process.`",
            log=(option, f"Successfully {option}ed a process in {extra}!"),
            self_destruct=2,
            reply=True,
        )
    else:
        await event.answer("`There is no process running for this message.`")
