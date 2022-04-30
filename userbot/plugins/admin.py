#
# PaperplaneRemix - A modular Telegram selfbot script
# Copyright (C) 2022, Avinash Reddy and the PaperplaneRemix contributors
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from datetime import timedelta

from userbot import client
from userbot.helper_funcs.time import string_to_secs
from userbot.utils.events import NewMessage
from userbot.utils.helpers import _humanfriendly_seconds, get_chat_link

plugin_category = "admin"


async def get_rights(
    event: NewMessage.Event,
    change_info: bool = False,
    post_messages: bool = False,
    edit_messages: bool = False,
    delete_messages: bool = False,
    ban_users: bool = False,
    invite_users: bool = False,
    pin_messages: bool = False,
    add_admins: bool = False,
) -> bool:
    """Return a bool according the required admin rights"""
    chat = await event.get_chat()
    if chat.creator:
        return True
    rights = {
        "change_info": change_info,
        "post_messages": post_messages,
        "edit_messages": edit_messages,
        "delete_messages": delete_messages,
        "ban_users": ban_users,
        "invite_users": invite_users,
        "pin_messages": pin_messages,
        "add_admins": add_admins,
    }
    required_rights = [
        getattr(chat.admin_rights, right, False)
        for right, required in rights.items()
        if required
    ]

    return all(required_rights)


@client.onMessage(
    command=("promote", plugin_category),
    outgoing=True,
    regex=r"promote(?: |$|\n)([\s\S]*)",
    require_admin=True,
)
async def promote(event: NewMessage.Event) -> None:
    """
    Promote a user in a group or channel.


    `{prefix}promote` in reply or **{prefix}promote user1 user2 [kwargs]**
        **Arguments:** `reason` and `title`
    """
    if not event.is_private and not await get_rights(event, add_admins=True):
        await event.answer("`I don't have rights to add admins in here!`")
        return
    elif event.is_private:
        await event.answer("`I can't promote users in private chats.`")
        return

    match = event.matches[0].group(1)
    args, kwargs = await client.parse_arguments(match)
    reason = kwargs.get("reason", None)
    title = kwargs.get("title", None)
    promoted, skipped = [], []

    if not args and event.reply_to_msg_id:
        reply = await event.get_reply_message()
        args.append(reply.sender_id)
    if not args:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
    for user in args:
        if isinstance(user, list):
            continue
        try:
            await client.edit_admin(
                entity=entity, user=user, is_admin=True, title=title
            )
            promoted.append(user)
        except Exception:
            skipped.append(user)
    if promoted:
        text = "`Successfully promoted:`\n"
        text += ", ".join(f"`{x}`" for x in promoted)
        if title:
            text += f"\n`Title:` `{title}`"
        if reason:
            text += f"\n`Reason:` `{reason}`"
        e2 = await get_chat_link(entity, event.id)
        log_msg = text + f"\n`Chat:` {e2}"
        await event.answer(text, log=("promote", log_msg))
    if skipped:
        text = "`Skipped users:`"
        text += ", ".join(f"`{x}`" for x in skipped)
        await event.answer(text, reply=True)


@client.onMessage(
    command=("demote", plugin_category),
    outgoing=True,
    regex=r"demote(?: |$|\n)([\s\S]*)",
    require_admin=True,
)
async def demote(event: NewMessage.Event) -> None:
    """
    Demote a user in a group or channel.


    `{prefix}demote` in reply or **{prefix}demote user1 user2 [kwargs]**
        **Arguments:** `reason`
    """
    if not event.is_private and not await get_rights(event, ban_users=True):
        await event.answer("`I don't have rights to remove admins in here!`")
        return
    elif event.is_private:
        await event.answer("`I can't demote users in private chats.`")
        return

    match = event.matches[0].group(1)
    args, kwargs = await client.parse_arguments(match)
    reason = kwargs.get("reason", None)
    demoted, skipped = [], []

    if not args and event.reply_to_msg_id:
        reply = await event.get_reply_message()
        args.append(reply.sender_id)
    if not args:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
    for user in args:
        if isinstance(user, list):
            continue
        try:
            await client.edit_admin(entity=entity, user=user, is_admin=False)
            demoted.append(user)
        except Exception:
            skipped.append(user)
    if demoted:
        text = "`Successfully demoted:`\n"
        text += ", ".join(f"`{x}`" for x in demoted)
        if reason:
            text += f"\n`Reason:` `{reason}`"
        e2 = await get_chat_link(entity, event.id)
        log_msg = text + f"\n`Chat:` {e2}"
        await event.answer(text, log=("demote", log_msg))
    if skipped:
        text = "`Skipped users:`"
        text += ", ".join(f"`{x}`" for x in skipped)
        await event.answer(text, reply=True)


@client.onMessage(
    command=("ban", plugin_category),
    outgoing=True,
    regex=r"ban(?: |$|\n)([\s\S]*)",
    require_admin=True,
)
async def ban(event: NewMessage.Event) -> None:
    """
    Ban a user in a group or channel.


    `{prefix}ban` in reply or **{prefix}ban user1 user2 [kwargs]**
        **Arguments:** `reason`
    """
    if not event.is_private and not await get_rights(event, ban_users=True):
        await event.answer("`I don't have rights to ban users in here!`")
        return
    elif event.is_private:
        await event.answer("`I can't ban users in private chats.`")
        return

    match = event.matches[0].group(1)
    args, kwargs = await client.parse_arguments(match)
    reason = kwargs.get("reason", None)
    banned, skipped = [], []

    if not args and event.reply_to_msg_id:
        reply = await event.get_reply_message()
        args.append(reply.sender_id)
    if not args:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
    for user in args:
        if isinstance(user, list):
            continue
        try:
            await client.edit_permissions(entity=entity, user=user, view_messages=False)
            banned.append(user)
        except Exception:
            skipped.append(user)
    if banned:
        text = "`Successfully banned:`\n"
        text += ", ".join(f"`{x}`" for x in banned)
        if reason:
            text += f"\n`Reason:` `{reason}`"
        e2 = await get_chat_link(entity, event.id)
        log_msg = text + f"\n`Chat:` {e2}"
        await event.answer(text, log=("ban", log_msg))
    if skipped:
        text = "`Skipped users:`"
        text += ", ".join(f"`{x}`" for x in skipped)
        await event.answer(text, reply=True)


@client.onMessage(
    command=("unban", plugin_category),
    outgoing=True,
    regex=r"unban(?: |$|\n)([\s\S]*)",
    require_admin=True,
)
async def unban(event: NewMessage.Event) -> None:
    """
    Un-ban a user in a group or channel.


    `{prefix}unban` in reply or **{prefix}unban user1 user2 [kwargs]**
        **Arguments:** `reason`
    """
    if not event.is_private and not await get_rights(event, ban_users=True):
        await event.answer("`I don't have rights to un-ban users in here!`")
        return
    elif event.is_private:
        await event.answer("`I can't un-ban users in private chats.`")
        return

    match = event.matches[0].group(1)
    args, kwargs = await client.parse_arguments(match)
    reason = kwargs.get("reason", None)
    unbanned, skipped = [], []

    if not args and event.reply_to_msg_id:
        reply = await event.get_reply_message()
        args.append(reply.sender_id)
    if not args:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
    for user in args:
        if isinstance(user, list):
            continue
        try:
            await client.edit_permissions(
                entity=entity,
                user=user,
                view_messages=True,
                send_messages=True,
                send_media=True,
                send_stickers=True,
                send_gifs=True,
                send_games=True,
                send_inline=True,
                send_polls=True,
            )
            unbanned.append(user)
        except Exception:
            skipped.append(user)
    if unbanned:
        text = "`Successfully unbanned:`\n"
        text += ", ".join(f"`{x}`" for x in unbanned)
        if reason:
            text += f"\n`Reason:` `{reason}`"
        e2 = await get_chat_link(entity, event.id)
        log_msg = text + f"\n`Chat:` {e2}"
        await event.answer(text, log=("unban", log_msg))
    if skipped:
        text = "`Skipped users:`"
        text += ", ".join(f"`{x}`" for x in skipped)
        await event.answer(text, reply=True)


@client.onMessage(
    command=("kick", plugin_category),
    outgoing=True,
    regex=r"kick(?: |$|\n)([\s\S]*)",
    require_admin=True,
)
async def kick(event: NewMessage.Event) -> None:
    """
    Kick a user in a group or channel.


    `{prefix}kick` in reply or **{prefix}kick user1 user2 [kwargs]**
        **Arguments:** `reason`
    """
    if not event.is_private and not await get_rights(event, ban_users=True):
        await event.answer("`I don't have rights to kick users in here!`")
        return
    elif event.is_private:
        await event.answer("`I can't kick users in private chats.`")
        return

    match = event.matches[0].group(1)
    args, kwargs = await client.parse_arguments(match)
    reason = kwargs.get("reason", None)
    kicked, skipped = [], []

    if not args and event.reply_to_msg_id:
        reply = await event.get_reply_message()
        args.append(reply.sender_id)
    if not args:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
    for user in args:
        if isinstance(user, list):
            continue
        try:
            await client.kick_participant(entity=entity, user=user)
            kicked.append(user)
        except Exception:
            skipped.append(user)
    if kicked:
        text = "`Successfully kicked:`\n"
        text += ", ".join(f"`{x}`" for x in kicked)
        if reason:
            text += f"\n`Reason:` `{reason}`"
        e2 = await get_chat_link(entity, event.id)
        log_msg = text + f"\n`Chat:` {e2}"
        await event.answer(text, log=("kick", log_msg))
    if skipped:
        text = "`Skipped users:`"
        text += ", ".join(f"`{x}`" for x in skipped)
        await event.answer(text, reply=True)


@client.onMessage(
    command=("mute", plugin_category),
    outgoing=True,
    regex=r"mute(?: |$|\n)([\s\S]*)",
    require_admin=True,
)
async def mute(event: NewMessage.Event) -> None:
    """
    Mute a user in a group or channel.


    `{prefix}mute` in reply or **{prefix}mute user1 user2 [kwargs]**
        **Arguments:** `reason`
    """
    if not event.is_private and not await get_rights(event, ban_users=True):
        await event.answer("`I don't have rights to mute users in here!`")
        return
    elif event.is_private:
        await event.answer("`I can't mute users in private chats.`")
        return

    match = event.matches[0].group(1)
    args, kwargs = await client.parse_arguments(match)
    reason = kwargs.get("reason", None)
    muted, skipped = [], []

    if not args and event.reply_to_msg_id:
        reply = await event.get_reply_message()
        args.append(reply.sender_id)
    if not args:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
    for user in args:
        if isinstance(user, list):
            continue
        try:
            await client.edit_permissions(entity=entity, user=user, send_messages=False)
            muted.append(user)
        except Exception:
            skipped.append(user)
    if muted:
        text = "`Successfully muted:`\n"
        text += ", ".join(f"`{x}`" for x in muted)
        if reason:
            text += f"\n`Reason:` `{reason}`"
        e2 = await get_chat_link(entity, event.id)
        log_msg = text + f"\n`Chat:` {e2}"
        await event.answer(text, log=("mute", log_msg))
    if skipped:
        text = "`Skipped users:`"
        text += ", ".join(f"`{x}`" for x in skipped)
        await event.answer(text, reply=True)


@client.onMessage(
    command=("unmute", plugin_category),
    outgoing=True,
    regex=r"unmute(?: |$|\n)([\s\S]*)",
    require_admin=True,
)
async def unmute(event: NewMessage.Event) -> None:
    """
    Un-mute a user in a group or channel.


    `{prefix}unmute` in reply or **{prefix}unmute user1 user2 [kwargs]**
        **Arguments:** `reason`
    """
    if not event.is_private and not await get_rights(event, ban_users=True):
        await event.answer("`I don't have rights to un-mute users in here!`")
        return
    elif event.is_private:
        await event.answer("`I can't un-mute users in private chats.`")
        return

    match = event.matches[0].group(1)
    args, kwargs = await client.parse_arguments(match)
    reason = kwargs.get("reason", None)
    unmuted, skipped = [], []

    if not args and event.reply_to_msg_id:
        reply = await event.get_reply_message()
        args.append(reply.sender_id)
    if not args:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
    for user in args:
        if isinstance(user, list):
            continue
        try:
            await client.edit_permissions(entity=entity, user=user, send_messages=True)
            unmuted.append(user)
        except Exception:
            skipped.append(user)
    if unmuted:
        text = "`Successfully unmuted:`\n"
        text += ", ".join(f"`{x}`" for x in unmuted)
        if reason:
            text += f"\n`Reason:` `{reason}`"
        e2 = await get_chat_link(entity, event.id)
        log_msg = text + f"\n`Chat:` {e2}"
        await event.answer(text, log=("unmute", log_msg))
    if skipped:
        text = "`Skipped users:`"
        text += ", ".join(f"`{x}`" for x in skipped)
        await event.answer(text, reply=True)


@client.onMessage(
    command=("tmute", plugin_category),
    outgoing=True,
    regex=r"tmute(?: |$|\n)([\s\S]*)",
    require_admin=True,
)
async def tmute(event: NewMessage.Event) -> None:
    """
    Temporary mute a user in a group or channel.


    `{prefix}tmute` in reply or **{prefix}tmute user1 user2 [kwargs]**
        **Arguments:** `reason` and `time`
    """
    if not event.is_private and not await get_rights(event, ban_users=True):
        await event.answer("`I don't have rights to mute users in here!`")
        return
    elif event.is_private:
        await event.answer("`I can't t-mute users in private chats.`")
        return

    match = event.matches[0].group(1)
    args, kwargs = await client.parse_arguments(match)
    reason = kwargs.get("reason", None)
    period = kwargs.get("time", None)
    if not period:
        await event.answer("`Specify the time by using time=<n>`")
        return
    period = await string_to_secs(period)
    tmuted, skipped = [], []

    if not args and event.reply_to_msg_id:
        reply = await event.get_reply_message()
        args.append(reply.sender_id)
    if not args:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
    for user in args:
        if isinstance(user, list):
            continue
        try:
            await client.edit_permissions(
                entity=entity,
                user=user,
                until_date=timedelta(seconds=period),
                send_messages=False,
            )
            tmuted.append(user)
        except Exception:
            skipped.append(user)
    if tmuted:
        text = "`Successfully tmuted:`\n"
        text += ", ".join(f"`{x}`" for x in tmuted)
        text += f"\n`Time:` `{await _humanfriendly_seconds(period)}`"
        if reason:
            text += f"\n`Reason:` `{reason}`"
        e2 = await get_chat_link(entity, event.id)
        log_msg = text + f"\n`Chat:` {e2}"
        await event.answer(text, log=("tmute", log_msg))
    if skipped:
        text = "`Skipped users:`"
        text += ", ".join(f"`{x}`" for x in skipped)
        await event.answer(text, reply=True)


@client.onMessage(
    command=("tban", plugin_category),
    outgoing=True,
    regex=r"tban(?: |$|\n)([\s\S]*)",
    require_admin=True,
)
async def tban(event: NewMessage.Event) -> None:
    """
    Temporary ban a user in a group or channel.


    `{prefix}tban` in reply or **{prefix}tban user1 user2 [kwargs]**
        **Arguments:** `reason` and `time`
    """
    if not event.is_private and not await get_rights(event, ban_users=True):
        await event.answer("`I don't have rights to t-ban users in here!`")
        return
    elif event.is_private:
        await event.answer("`I can't t-ban users in private chats.`")
        return

    match = event.matches[0].group(1)
    args, kwargs = await client.parse_arguments(match)
    reason = kwargs.get("reason", None)
    period = kwargs.get("time", None)
    if not period:
        await event.answer("`Specify the time by using time=<n>`")
        return
    period = await string_to_secs(period)
    tbanned, skipped = [], []

    if not args and event.reply_to_msg_id:
        reply = await event.get_reply_message()
        args.append(reply.sender_id)
    if not args:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
    for user in args:
        if isinstance(user, list):
            continue
        try:
            await client.edit_permissions(
                entity=entity,
                user=user,
                until_date=timedelta(seconds=period),
                view_messages=False,
            )
            tbanned.append(user)
        except Exception:
            skipped.append(user)
    if tbanned:
        text = "`Successfully tbanned:`\n"
        text += ", ".join(f"`{x}`" for x in tbanned)
        text += f"\n`Time:` `{await _humanfriendly_seconds(period)}`"
        if reason:
            text += f"\n`Reason:` `{reason}`"
        e2 = await get_chat_link(entity, event.id)
        log_msg = text + f"\n`Chat:` {e2}"
        await event.answer(text, log=("tban", log_msg))
    if skipped:
        text = "`Skipped users:`"
        text += ", ".join(f"`{x}`" for x in skipped)
        await event.answer(text, reply=True)


@client.onMessage(
    command=("pin", plugin_category),
    outgoing=True,
    regex=r"(loud)?pin$",
    require_admin=True,
)
async def pin(event: NewMessage.Event) -> None:
    """Pin the message at the top of the group or channel."""
    if not event.is_private and not await get_rights(event, pin_messages=True):
        await event.answer("`I don't have rights to pin messages in here!`")
        return
    elif event.is_private:
        await event.answer("`I can't pin messages in private chats.`")
        return

    notify = bool(event.matches[0].group(1))

    if not event.reply_to_msg_id:
        await event.answer("`I can't pin the void!`")
        return

    entity = await event.get_chat()
    try:
        await client.pin_message(
            entity=entity, message=event.reply_to_msg_id, notify=notify
        )
        text = "`Successfully pinned!`\n"
        text += f"`Loud-Pin:` `{'Yes' if notify else 'No'}`\n"
    except Exception:
        text = "`Failed to pin the message!`\n"
    e2 = await get_chat_link(event, event.reply_to_msg_id)
    log_msg = text + f"`Chat:` {e2}"
    await event.answer(text, log=("pin", log_msg))
