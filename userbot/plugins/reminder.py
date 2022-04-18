#
# PaperplaneRemix - A modular Telegram selfbot script
# Copyright (C) 2022, Avinash Reddy and the PaperplaneRemix contributors
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import datetime

from userbot import client
from userbot.helper_funcs.time import string_to_secs
from userbot.utils.helpers import _humanfriendly_seconds, get_chat_link
from userbot.utils.events import NewMessage


plugin_category = "reminder"


@client.onMessage(
    command=("remindme/remindhere", plugin_category),
    outgoing=True,
    regex=r"remind(me|here)(?: |$)(\w+)?(?: |$|\n)([\s\S]*)",
)
async def remindme(event: NewMessage.Event) -> None:
    """
    Set a reminder (scheduled message) to be sent in n amount of time.


    **{prefix}remindme (time) (text)** or **{prefix}remindhere (time) (text)**
        **Example:** **{prefix}remindme 2h gts**
    """
    arg = event.matches[0].group(1)
    time = event.matches[0].group(2)
    text = event.matches[0].group(3)
    media = False

    if not time:
        await event.answer("Remind you when?")
        return
    elif not text and not event.reply_to_msg_id:
        await event.answer("Remind you with what?")
        return

    seconds = await string_to_secs(time)
    if event.reply_to_msg_id:
        reply = await event.get_reply_message()
        media = True
    if arg == "here":
        entity = event.chat_id
    else:
        entity = client.config["userbot"].getint("logger_group_id", "self")
    entity = await client.get_entity(entity)

    if seconds >= 13:
        await client.send_message(
            entity=entity,
            message=reply if media else text,
            schedule=datetime.timedelta(seconds=seconds),
        )
        extra = await get_chat_link(entity)
        human_time = await _humanfriendly_seconds(seconds)
        message = f"`Reminder will be sent in` {extra} `after {human_time}.`"
        await event.answer(
            message,
            self_destruct=2,
            log=("remindme", f"Set a reminder in {extra}.\nETA: {human_time}"),
        )
    else:
        await event.answer("`No kan do. ma'am. Minimum time should be 13s.`")
