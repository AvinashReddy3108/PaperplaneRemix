#
# PaperplaneRemix - A modular Telegram selfbot script
# Copyright (C) 2022, Avinash Reddy and the PaperplaneRemix contributors
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import logging
import re
from typing import Union

from telethon.tl import types

from ..utils.events import NewMessage

LOGGER = logging.getLogger(__name__)


async def get_user_from_msg(event: NewMessage.Event) -> Union[int, str, None]:
    """A legacy helper function to get user object from the event."""
    user = None
    match = event.matches[0].group(1)

    if event.reply_to_msg_id and not match:
        return (await event.get_reply_message()).sender_id

    if match == "me":
        return (await event.client.get_me()).id
    if match == "this":
        match = str(event.chat.id)

    if event.entities:
        for entity in event.entities:
            if isinstance(entity, types.MessageEntityMentionName):
                return entity.user_id
            elif isinstance(entity, types.MessageEntityMention):
                offset = entity.offset
                length = entity.length
                maxlen = offset + length
                return event.text[offset:maxlen]

    if match:
        if isinstance(match, str) and match.isdigit():
            user = int(match.strip())
        else:
            user = match.strip()

    return user


async def get_entity_from_msg(
    event: NewMessage.Event,
) -> tuple[Union[None, types.User], Union[None, bool, str], Union[None, bool, str]]:
    """Get a User entity and/or a reason from the event's regex pattern"""
    exception = False
    entity = None
    match = event.matches[0].group(1)

    # TODO: Find better logic to differentiate user and reason
    pattern = re.compile(r"(@?\w+|\d+)(?: |$)(.*)")
    user = pattern.match(match)[1] if match else None
    extra = pattern.match(match)[2] if match else None
    reply = await event.get_reply_message()

    if reply and not (user and extra):
        user = reply.sender_id
        extra = match.strip()

    user = int(user) if isinstance(user, str) and user.isdigit() else user
    if not user:
        return None, None, "Couldn't fetch an entity from your message!"

    try:
        entity = await event.client.get_entity(user)
    except Exception as e:
        exception = True
        LOGGER.exception(e)

    return entity, extra, exception
