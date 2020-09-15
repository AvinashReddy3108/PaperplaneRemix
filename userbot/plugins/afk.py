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

import datetime
import os
import time
import random

from telethon.events import StopPropagation
from telethon.tl import types, functions
from typing import Tuple

from userbot import client
from userbot.plugins import plugins_data
from userbot.utils.helpers import _humanfriendly_seconds, get_chat_link
from userbot.utils.events import NewMessage

DEFAULT_MUTE_SETTINGS = types.InputPeerNotifySettings(
    silent=True, mute_until=datetime.timedelta(days=365)
)

AFK = plugins_data.AFK
AFK.privates = plugins_data.load_data("userbot_afk_privates")
AFK.groups = plugins_data.load_data("userbot_afk_groups")
AFK.sent = plugins_data.load_data("userbot_afk_sent")

going_afk = "`AFK AF!`"
going_afk_reason = "`Going AFK!`" + "\n**Reason:** __{reason}.__"
not_afk = "`I'm back!`"
currently_afk_reason = "`I'm currently AFK!`\
    \n**Last seen:** __{elapsed} ago.__\
    \n**Reason:** __{reason}.__"

AFKMEMEZ = [
    "You missed me, next time aim better.",
    "Me no here, Me go bye.\nLeave me message. Me reply.",
    "I'll be back in a few minutes and if I'm not...,\nwait longer.",
    "I'm not here right now, so I'm probably somewhere else.",
    "Roses are red, violets are blue.\
        \nLeave me a message, and I'll get back to you.",
    "I'll be right back,\nbut if I'm not right back,\nI'll be back later.",
    "If you haven't figured it out already,\nI'm not here.",
    "Hello, welcome to my away message, how may I ignore you today?",
    "You know the drill, you leave a message, and I'll ignore it.",
    "I'm away from the keyboard at the moment,\
        \nbut if you'll scream loud enough at your screen,\
        \nI might just hear you.",
    "I went that way\n---->",
    "<Insert witty away message here.>",
    "This is an away message and I am away... so leave a message.",
    "I went this way\n<----",
    "If I were here,\nI'd tell you where I am.\
        \nBut I'm not,\nso ask me when I return...",
    "I am away!\nI don't know when I'll be back!\
        \nHopefully a few minutes from now!",
    "I bet you were expecting an away message!",
    "Life is so short, there are so many things to do...\
        \nI'm away doing one of them..",
    "I am not here right now...\nbut if I was...\n\nwouldn't that be awesome?",
]


@client.onMessage(command="afk", outgoing=True, regex=r"afk(?: |$)(.*)?$")
async def awayfromkeyboard(event: NewMessage.Event) -> None:
    """
    Set your status as AFK until you send a message again.


    **{prefix}afk** or **{prefix}afk (reason)**
        **Example:** `{prefix}afk` or `{prefix}afk sleeping`
    """
    arg = event.matches[0].group(1)
    curtime = time.time().__str__()
    os.environ["userbot_afk"] = f"{curtime}/{event.chat_id}/{event.id}"
    extra = await get_chat_link(event, event.id)
    log = ("afk", f"You just went AFK in {extra}!")
    if arg:
        arg = arg.strip()
        os.environ["userbot_afk_reason"] = arg
        await event.resanswer(
            going_afk_reason,
            plugin="afk",
            name="going_afk_reason",
            formats={"reason": arg},
            log=log,
        )
    else:
        await event.resanswer(going_afk, plugin="afk", name="going_afk", log=log)
    raise StopPropagation


@client.onMessage(outgoing=True, forwards=None)
async def out_listner(event: NewMessage.Event) -> None:
    """Handle your AFK status by listening to new outgoing messages."""
    userbot_afk = os.environ.pop("userbot_afk", False)
    if event.from_scheduled or not userbot_afk:
        return

    os.environ.pop("userbot_afk_reason", None)
    _, chat, msg = userbot_afk.split("/")
    await client.delete_messages(int(chat), int(msg))

    def_text = "`I received no messages nor was tagged while I was away.`"
    pr_text = ""
    pr_log = ""
    gr_text = ""
    gr_log = ""

    if AFK.privates:
        total_mentions = 0
        to_log = []
        pr_log = "**Pings/PMs:**\n"
        for key, value in AFK.privates.items():
            await _update_notif_settings(key, value["PeerNotifySettings"])
            total_mentions += len(value["mentions"])
            msg = "  `{} total mentions from` [{}](tg://user?id={})"
            to_log.append(msg.format(len(value["mentions"]), value["title"], key))

        pr_text = "`Received {} message{} from {} private chat{}.`".format(
            *(await _correct_grammer(total_mentions, len(AFK.privates)))
        )
        pr_log += "\n\n".join("  " + t for t in to_log)
    if AFK.groups:
        total_mentions = 0
        to_log = []
        gr_log = "\n**Tags/Mentions:**\n"
        for key, value in AFK.groups.items():
            await _update_notif_settings(key, value["PeerNotifySettings"])
            total_mentions += len(value["mentions"])
            chat_msg_id = f"https://t.me/c/{key}/{value['unread_from']}"
            msg = f"[{value['title']}]({chat_msg_id}):"
            msg += "\n    `Mentions:` "
            mentions = []
            for i in range(len(value["mentions"])):
                msg_id = value["mentions"][i]
                mentions.append(f"[{i + 1}](https://t.me/c/{key}/{msg_id})")
            msg += ",   ".join(mentions) + "."
            to_log.append(msg)

        gr_text = "`Received {} mention{} from {} group{}.`".format(
            *(await _correct_grammer(total_mentions, len(AFK.groups)))
        )
        gr_log += "\n\n".join("  " + t for t in to_log)

    main_text = "\n\n".join([pr_text, gr_text]).strip()
    if not client.logger:
        main_text += "\n`Use a logger group for more detailed AFK mentions!`"
    status = await event.resanswer(
        not_afk, plugin="afk", name="not_afk", reply_to=event.id, self_destruct=4
    )
    await event.answer(
        main_text or def_text,
        reply_to=status.id,
        self_destruct=4,
        log=("afk", "\n".join([pr_log, gr_log]).strip() or def_text),
    )

    for chat, msg in AFK.sent.items():
        msgs = [m for m, _ in msg]
        await client.delete_messages(chat, msgs)
    AFK.privates.clear()
    AFK.groups.clear()
    AFK.sent.clear()


@client.onMessage(incoming=True, edited=False)
async def inc_listner(event: NewMessage.Event) -> None:
    """Handle tags and new messages by listening to new incoming messages."""
    sender = await event.get_sender()
    if event.from_scheduled or (isinstance(sender, types.User) and sender.bot):
        return

    afk = os.environ.get("userbot_afk", False)
    if not (afk and (event.is_private or event.mentioned)):
        return

    since = datetime.datetime.fromtimestamp(
        float(afk.split("/")[0]), tz=datetime.timezone.utc
    )
    now = datetime.datetime.now(datetime.timezone.utc)
    reason = os.environ.get("userbot_afk_reason", False)
    elapsed = await _humanfriendly_seconds((now - since).total_seconds())
    chat = await event.get_chat()
    if event.is_private:
        await _append_msg(AFK.privates, chat.id, event.id)
    else:
        await _append_msg(AFK.groups, chat.id, event.id)

    if chat.id in AFK.sent:
        # Floodwait prevention, in case some retards spam tag/PM you.
        timeout = random.randint(15, 60)
        if round((now - AFK.sent[chat.id][-1][1]).total_seconds()) <= timeout:
            return

    if reason:
        result = await event.resanswer(
            currently_afk_reason,
            plugin="afk",
            name="currently_afk_reason",
            formats={"elapsed": elapsed, "reason": reason},
            reply_to=event if not event.is_private else None,
        )
    else:
        result = await event.resanswer(
            f"**{random.choice(AFKMEMEZ)}**\n__Last seen: {elapsed} ago.__",
            plugin="afk",
            name="currently_afk",
            formats={"elapsed": elapsed},
            reply_to=event if not event.is_private else None,
        )
    AFK.sent.setdefault(chat.id, []).append((result.id, result.date))


async def _append_msg(variable: dict, chat: int, event: int) -> None:
    if chat in variable:
        variable[chat]["mentions"].append(event)
    else:
        notif = await client(functions.account.GetNotifySettingsRequest(peer=chat))
        notif = types.InputPeerNotifySettings(**vars(notif))
        await _update_notif_settings(chat)
        async for dialog in client.iter_dialogs():
            if chat == dialog.entity.id:
                title = getattr(dialog, "title", dialog.name)
                unread_count = dialog.unread_count
                last_msg = dialog.message.id
                break
        x = 1
        messages = []
        async for message in client.iter_messages(chat, max_id=last_msg):
            if x >= unread_count:
                if not messages:
                    messages.append(message.id)
                break
            if not message.out:
                x += 1
                messages.append(message.id)
        variable[chat] = {
            "title": title,
            "unread_from": messages[-1],
            "mentions": [event],
            "PeerNotifySettings": notif,
        }
        messages.clear()


async def _update_notif_settings(
    peer: int, settings: types.InputPeerNotifySettings = DEFAULT_MUTE_SETTINGS
) -> None:
    await client(
        functions.account.UpdateNotifySettingsRequest(peer=peer, settings=settings)
    )


async def _correct_grammer(mentions: int, chats: int) -> Tuple[str, str, str, str]:
    a1 = "one" if mentions == 1 else mentions
    a2 = "" if mentions == 1 else "s"
    a3 = "one" if chats == 1 else chats
    a4 = "" if chats == 1 else "s"
    return a1, a2, a3, a4
