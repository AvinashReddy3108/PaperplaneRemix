# FBan Helper Extension for PaperplaneRemix.
# Copyright (C) 2020 Avinash Reddy <https://github.com/AvinashReddy3108>

import asyncio
from userbot import client, LOGGER
from userbot.utils.events import NewMessage
from userbot.utils.helpers import get_chat_link

plugin_category = "fedadmin"


@client.onMessage(command=("fban", plugin_category),
                  outgoing=True,
                  regex=r"fban(?: |$|\n)([\s\S]*)")
async def fban(event: NewMessage.Event) -> None:
    """Ban a user in all your federations."""
    match = event.matches[0].group(1)
    args, kwargs = await client.parse_arguments(match)
    reason = kwargs.get('reason', None)
    skipped = {}
    fbanned = []

    fban_admin_chats_list = client.config['userbot'].get(
        'fban_admin_chats', None)
    if fban_admin_chats_list is None:
        await event.answer(
            "`Atleast one fedadmin chat should be set up for this to work!`")
        return
    
    fban_admin_chats = set(int(x) for x in fban_admin_chats_list.split(','))

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
        spammer = await client.get_entity(user)
        success = 0
        failed = []
        try:
            for chat in fban_admin_chats:
                async with client.conversation(chat, timeout=5,
                                               exclusive=True) as conv:
                    if event.reply_to_msg_id:
                        reply = await event.get_reply_message()
                        await reply.forward_to(chat)
                    await conv.send_message(f"/fban {spammer.id} {reason}")
                    resp = await conv.get_response()
                    LOGGER.debug(f"FBan: {resp.text}")
                    await client.send_read_acknowledge(conv.chat_id, resp)
                    if "New FedBan" not in resp.text:
                        failed.append(chat)
                        skipped.update({user: failed})
                        continue
                await asyncio.sleep(0.3)
                success += 1
                fbanned.append(user)
        except Exception as error:
            LOGGER.debug(f"FBan failed: {error}")
            failed.append(user)
            skipped.update({user: failed})
    if fbanned:
        text = f"`Successfully Fedbanned:`\n"
        text += ', '.join((f'`{x}`' for x in fbanned))
        if reason:
            text += f"\n`Reason:` `{reason}`"
        e2 = await get_chat_link(entity, event.id)
        log_msg = text + f"\n`Chat:` {e2}"
        await event.answer(text, log=("fban", log_msg))
    if skipped:
        text = "`Failed FBan requests:`"
        text += ', '.join((f"`{x}: [{', '.join(y)}]`" for x, y in skipped))
        await event.answer(text, reply=True)
