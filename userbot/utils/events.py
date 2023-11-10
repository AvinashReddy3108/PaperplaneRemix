#
# PaperplaneRemix - A modular Telegram selfbot script
# Copyright (C) 2022, Avinash Reddy and the PaperplaneRemix contributors
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import re
from typing import Tuple

from telethon import events
from telethon.tl import custom, functions, types


async def answer(self, *args, **kwargs):
    if self._client:
        return await self._client.answer(
            await self.get_input_chat(), event=self, *args, **kwargs
        )


async def resanswer(self, *args, **kwargs):
    if self._client:
        return await self._client.resanswer(
            await self.get_input_chat(), event=self, *args, **kwargs
        )


custom.Message.answer = answer
custom.Message.resanswer = resanswer


@events.common.name_inner_event
class NewMessage(events.NewMessage):
    """Custom NewMessage event inheriting the default Telethon event"""

    def __init__(
        self,
        disable_prefix: bool = None,
        regex: Tuple[str, int] or str = None,
        require_admin: bool = None,
        inline: bool = False,
        **kwargs
    ):
        """Overriding the default init to add additional attributes"""
        super().__init__(**kwargs)

        if regex:
            if isinstance(regex, tuple):
                exp, flags = regex
                if isinstance(exp, tuple):
                    raise TypeError("Make sure you're using a string for a pattern!")
                self.regex = (exp, flags)
            elif isinstance(regex, str):
                self.regex = (regex, 0)
            else:
                raise TypeError("Invalid regex type given!")
        else:
            self.regex = regex

        self.disable_prefix = disable_prefix
        self.require_admin = require_admin
        self.inline = inline

    def filter(self, event):
        """Overriding the default filter to check additional values"""
        _event = super().filter(event)
        if not _event:
            return

        if self.inline is not None and bool(self.inline) != bool(
            event.message.via_bot_id
        ):
            return

        if event._client.prefix:
            prefix = re.escape(event._client.prefix)
        else:
            prefix = r"[^/!#@\$A-Za-z0-9\-]"

        if self.regex:
            exp, flags = self.regex
            exp = exp.format(prefix=prefix)

            pattern = (
                re.compile(exp, flags=flags).finditer
                if self.disable_prefix
                else re.compile(f"(?i)^{prefix}{exp}", flags=flags).finditer
            )

            text = event.message.message or ""
            if matches := list(pattern(text)) or None:
                event.matches = matches

            else:
                return
        if self.require_admin:
            text = "`I need admin rights to be able to use this command!`"
            if not isinstance(event._chat_peer, types.PeerUser):
                is_creator = False
                is_admin = False
                creator = hasattr(event.chat, "creator")
                admin_rights = hasattr(event.chat, "admin_rights")
                if not creator and not admin_rights:
                    event.chat = event._client.loop.create_task(event.get_chat())

                if self.incoming:
                    try:
                        p = event._client.loop.create_task(
                            event._client(
                                functions.channels.GetParticipantRequest(
                                    channel=event.chat_id, user_id=event.sender_id
                                )
                            )
                        )
                        participant = p.participant
                    except Exception:
                        participant = None
                    if isinstance(participant, types.ChannelParticipantCreator):
                        is_creator = True
                    if isinstance(participant, types.ChannelParticipantAdmin):
                        is_admin = True
                else:
                    is_creator = event.chat.creator
                    is_admin = event.chat.admin_rights

                if not is_creator and not is_admin:
                    if self.outgoing and event.message.out:
                        event._client.loop.create_task(event.answer(text))
                    elif self.incoming and not event.message.out:
                        event._client.loop.create_task(event.answer(text, reply=True))
                    return
        return event


@events.common.name_inner_event
class MessageEdited(NewMessage):
    """Custom MessageEdited event inheriting the custom NewMessage event"""

    class Event(NewMessage.Event):
        """Overriding the default Event which inherits Telethon's NewMessage"""

        pass  # Required if we want a different name for it

    @classmethod
    def build(cls, update, others=None, self_id=None):
        """
        Required to check if message is edited, double events.
        Note: Don't handle UpdateEditChannelMessage from channels since the
              update doesn't show which user edited the message
        """
        if isinstance(update, types.UpdateEditMessage):
            return cls.Event(update.message)
        elif isinstance(update, types.UpdateEditChannelMessage):
            if (
                update.message.edit_date
                and update.message.is_channel
                and not update.message.is_group
            ):
                return
            return cls.Event(update.message)
