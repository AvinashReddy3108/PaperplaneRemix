#
# PaperplaneRemix - A modular Telegram selfbot script
# Copyright (C) 2022, Avinash Reddy and the PaperplaneRemix contributors
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


from userbot import client
from userbot.utils.events import NewMessage
from userbot.utils.helpers import get_chat_link

plugin_category = "user"


async def _offset(event: NewMessage.Event) -> int:
    if event.reply_to_msg_id:
        return event.reply_to_msg_id - 1
    return event.message.id


@client.onMessage(
    command=("purge", "admin"),
    require_admin=True,
    outgoing=True,
    regex=r"purge(?: |$)(.*)",
)
async def purge(event: NewMessage.Event) -> None:
    """
    Delete (AKA purge) multiple messages from a chat all together.


    `{prefix}purge` or **{prefix}purge [kwargs]**
        **Arguments:** `amount` and `skip`
        **Example:** `{prefix}purge amount=10 skip=2`
    """
    if (event.is_channel or event.is_group) and not (
        event.chat.creator or event.chat.admin_rights.delete_messages
    ):
        await event.answer("`I don't have rights to delete messages in here!`")
        return

    entity = await event.get_chat()
    _, kwargs = await client.parse_arguments(event.matches[0].group(1) or "")
    amount = kwargs.get("amount", None)
    skip = kwargs.get("skip", 0)

    if not event.reply_to_msg_id and not amount:
        await event.answer("`Purged the void.`", self_destruct=2)
        return

    reverse = bool(event.reply_to_msg_id)
    messages = await client.get_messages(
        entity,
        limit=int(amount) + skip if amount else None,
        max_id=event.message.id,
        offset_id=await _offset(event),
        reverse=reverse,
    )
    messages = messages[skip:]

    await client.delete_messages(entity, messages)
    extra = await get_chat_link(entity)
    await event.answer(
        f"`Successfully deleted {len(messages)} message(s)!`",
        self_destruct=2,
        log=("purge", f"Purged {len(messages)} message(s) in {extra}"),
    )


@client.onMessage(
    command=("delme", plugin_category), outgoing=True, regex=r"delme(?: |$)(.*)"
)
async def delme(event: NewMessage.Event) -> None:
    """
    Delete YOUR messages in a chat. Similar to purge's logic.


    `{prefix}delme` or **{prefix}delme [kwargs]**
        **Arguments:** `amount` and `skip`
        **Example:** `{prefix}delme amount=10 skip=2`
    """
    entity = await event.get_chat()
    _, kwargs = await client.parse_arguments(event.matches[0].group(1) or "")
    amount = kwargs.get("amount", None)
    skip = kwargs.get("skip", 0)

    if not amount:
        amount = 1 if not event.reply_to_msg_id else None

    reverse = bool(event.reply_to_msg_id)
    messages = await client.get_messages(
        entity,
        limit=int(amount) + skip if amount else None,
        max_id=event.message.id,
        offset_id=await _offset(event),
        reverse=reverse,
        from_user="me",
    )
    messages = messages[skip:]

    await client.delete_messages(entity, messages)
    await event.answer(
        f"`Successfully deleted {len(messages)} message(s)!`",
        self_destruct=2,
    )


@client.onMessage(command="del", outgoing=True, regex=r"del$")
async def delete(event: NewMessage.Event) -> None:
    """
    Delete your or other's replied to message.


    `{prefix}del` in reply to your message
    """
    reply = await event.get_reply_message()
    if not reply:
        await event.answer("`There's nothing for me to delete!`")
        return

    if reply.sender_id != (await client.get_me()).id:
        if event.is_group and (
            event.chat.creator or event.chat.admin_rights.delete_messages
        ):
            await reply.delete()
        else:
            await event.answer("`I don't have enough rights in here!`")
            return
    else:
        await reply.delete()
    await event.delete()
