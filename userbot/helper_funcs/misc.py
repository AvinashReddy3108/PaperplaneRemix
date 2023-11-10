#
# PaperplaneRemix - A modular Telegram selfbot script
# Copyright (C) 2022, Avinash Reddy and the PaperplaneRemix contributors
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from typing import Union

from telethon.tl import types

from ..utils.client import UserBotClient
from ..utils.helpers import get_chat_link

ChatBannedRights = {
    "until_date": "Banned until:",
    "view_messages": "Read messages:",
    "send_messages": "Send messages:",
    "send_media": "Send media:",
    "send_stickers": "Send stickers:",
    "send_gifs": "Send GIFs:",
    "send_games": "Send games:",
    "send_inline": "Send inline messages:",
    "embed_links": "Send embed links:",
    "send_polls": "Send polls:",
    "change_info": "Change info:",
    "invite_users": "Add users:",
    "pin_messages": "Pin messages:",
}

ChatAdminRights = {
    "change_info": "Change chat info:",
    "post_messages": "Post messages:",
    "edit_messages": "Edit messages:",
    "delete_messages": "Delete messages:",
    "ban_users": "Ban users:",
    "invite_users": "Invite users:",
    "pin_messages": "Pin messages:",
    "add_admins": "Add new admins:",
}


async def parse_admin_rights(AdminRights: types.ChatAdminRights) -> str:
    text = []
    for attr, string in ChatAdminRights.items():
        if right := getattr(AdminRights, attr, False):
            text.append(f"{string} {right}")
    return "\n".join(text)


async def parse_banned_rights(BannedRights: types.ChatBannedRights) -> str:
    text = []
    for attr, string in ChatBannedRights.items():
        if right := getattr(BannedRights, attr, False):
            if attr == "until_date":
                text.append(f"{string} {right.ctime()} (UTC)")
            else:
                text.append(f"{string} {right}")
    return "\n".join(text)


async def get_entity_info(
    arg: Union[types.ChatFull, types.ChannelFull]
) -> tuple[int, int, int, int, int, int]:
    creator, admins, bots, participants, kicked, banned = (
        None,
        None,
        None,
        None,
        None,
        None,
    )
    full_chat = arg.full_chat
    if isinstance(full_chat, types.ChannelFull):
        if hasattr(full_chat, "participants_count"):
            participants = full_chat.participants_count
        if hasattr(full_chat, "admins_count"):
            admins = full_chat.admins_count
        if hasattr(full_chat, "kicked_count"):
            kicked = full_chat.kicked_count
        if hasattr(full_chat, "banned_count"):
            banned = full_chat.banned_count
        if hasattr(full_chat, "bot_info"):
            bots = len(full_chat.bot_info)
    else:
        if hasattr(full_chat, "bot_info"):
            bots = len(full_chat.bot_info)
        if hasattr(full_chat, "participants"):
            admins, participants = 0, 0
            for p in full_chat.participants.participants:
                if isinstance(p, types.ChatParticipantCreator):
                    creator = p.user_id
                if isinstance(p, types.ChatParticipant):
                    participants += 1
                if isinstance(p, types.ChatParticipantAdmin):
                    admins += 1
    return creator, admins, bots, participants, kicked, banned


async def unparse_info(
    client: UserBotClient,
    creator: int,
    admins: int,
    bots: int,
    users: int,
    kicked: int,
    banned: int,
) -> str:
    text = ""
    if creator:
        c = await client.get_entity(creator)
        text += f"\n**Creator:** {await get_chat_link(c)}"
    if users:
        text += f"\n**Participants:** {users}"
    if admins:
        text += f"\n**Admins:** {admins}"
    if bots:
        text += f"\n**Bots:** {bots}"
    if kicked:
        text += f"\n**Kicked:** {kicked}"
    if banned:
        text += f"\n**Banned:** {banned}"
    return text


async def unparse_rights(title: str, rights: str) -> str:
    text = f"**{title}**"
    for right in rights.split("\n"):
        splat = right.split(":")
        text += f"\n  **{splat[0]}:** `{':'.join(splat[1:])}`"
    return text


async def resolve_channel(client: UserBotClient, channel: types.ChannelFull) -> str:
    text = ""
    default_banned_rights = None
    banned_rights = None
    admin_rights = None
    channel_type = "Channel"
    for c in channel.chats:
        if c.id == channel.full_chat.id:
            if c.megagroup:
                channel_type = "Megagroup"
            admin_rights = c.admin_rights
            banned_rights = c.banned_rights
            default_banned_rights = c.default_banned_rights
            break

    text += f"\n**{channel_type} ID:** `{channel.full_chat.id}`"
    info = await get_entity_info(channel)
    text += await unparse_info(client, *info)
    if admin_rights:
        parsed = await parse_admin_rights(admin_rights)
        unparsed = await unparse_rights("Admin rights:", parsed)
        text += f"\n{unparsed}"
    if banned_rights:
        parsed = await parse_banned_rights(banned_rights)
        unparsed = await unparse_rights("Banned rights:", parsed)
        text += f"\n{unparsed}"
    if default_banned_rights:
        parsed = await parse_banned_rights(default_banned_rights)
        unparsed = await unparse_rights("Default banned rights:", parsed)
        text += f"\n{unparsed}"
    return text


async def resolve_chat(client: UserBotClient, chat: types.ChatFull) -> str:
    text = f"\n**Chat ID:** `{chat.full_chat.id}``"
    info = await get_entity_info(chat)
    text += await unparse_info(client, *info)
    admin_rights = None
    default_banned_rights = None
    for c in chat.chats:
        if c.id == chat.full_chat.id:
            admin_rights = c.admin_rights
            default_banned_rights = c.default_banned_rights
            break
    if admin_rights:
        parsed = await parse_admin_rights(admin_rights)
        unparsed = await unparse_rights("Admin rights:", parsed)
        text += f"\n{unparsed}"
    if default_banned_rights:
        parsed = await parse_banned_rights(default_banned_rights)
        unparsed = await unparse_rights("Default banned rights:", parsed)
        text += f"\n{unparsed}"
    return text
