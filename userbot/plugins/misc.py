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

import aiohttp
import functools
import git
import io
import PIL
import re
import requests

from telethon import utils
from telethon.tl import functions, types

from userbot import client, LOGGER
from userbot.helper_funcs import misc
from userbot.utils.helpers import get_chat_link
from userbot.utils.events import NewMessage

plugin_category = "misc"
invite_links = {
    "private": re.compile(r"^(?:https?://)?(t\.me/joinchat/\w+)/?$"),
    "public": re.compile(r"^(?:https?://)?t\.me/(\w+)/?$"),
    "username": re.compile(r"^@?(\w{5,32})$"),
}
usernexp = re.compile(r"@(\w{3,32})\[(.+?)\]")
nameexp = re.compile(r"\[([\w\S]+)\]\(tg://user\?id=(\d+)\)\[(.+?)\]")


def removebg_post(API_KEY: str, media: bytes or str):
    image_parameter = "image_url" if isinstance(media, str) else "image_file"
    return requests.post(
        "https://api.remove.bg/v1.0/removebg",
        files={image_parameter: media},
        data={"size": "auto"},
        headers={"X-Api-Key": API_KEY},
    )


def dogbin_post(text: str):
    return requests.post(
        "https://del.dog/documents",
        data=text.encode("UTF-8") if isinstance(text, str) else text,
        headers={
            "Content-type": "text/plain",
            "Accept": "application/json",
            "charset": "utf-8",
        },
    )


@client.onMessage(
    command=("rmbg", plugin_category), outgoing=True, regex=r"r(m)?bg(?: |$)(.*)$"
)
async def rmbg(event: NewMessage.Event) -> None:
    """
    Remove the background from an image or sticker.


    `{prefix}rmbg` or **{prefix}rmbg (url)**
    """
    API_KEY = client.config["api_keys"].get("api_key_removebg", False)
    if not API_KEY:
        await event.answer("`I don't have an API key set for remove.bg!`")
        return

    match = event.matches[0].group(2)
    reply = await event.get_reply_message()

    if match:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(match) as response:
                    if not (
                        response.status == 200
                        and response.content_type.startswith("image/")
                    ):
                        await event.answer("`The provided link seems to be invalid.`")
                        return
            except aiohttp.client_exceptions.InvalidURL:
                await event.answer("`Invalid URL provided!`")
                return
            except Exception as e:
                exc = await client.get_traceback(e)
                await event.answer(f"**Unknown exception:**\n```{exc}```")
                return
        media = match
    elif reply and reply.media:
        ext = utils.get_extension(reply.media)
        acceptable = [".jpg", ".png", ".bmp", ".tif", ".webp"]
        if ext not in acceptable:
            await event.answer("`Nice try, fool!`")
            return

        await event.answer("`Downloading media...`")
        media = io.BytesIO()
        await client.download_media(reply, media)
        if ext in [".bmp", ".tif", ".webp"]:
            new_media = io.BytesIO()
            try:
                pilImg = PIL.Image.open(media)
            except OSError as e:
                await event.answer(f"`OSError: {e}`")
                return
            pilImg.save(new_media, format="PNG")
            pilImg.close()
            media.close()
            media = new_media
    else:
        await event.answer("`Reply to a photo or provide a valid link.`")
        return

    response = await client.loop.run_in_executor(
        None, functools.partial(removebg_post, API_KEY, media.getvalue())
    )
    if not isinstance(media, str):
        media.close()
    if response.status_code == 200:
        await event.delete()
        image = io.BytesIO(response.content)
        image.name = "image.png"
        await event.answer(file=image, force_document=True, reply=True)
        image.close()
    else:
        error = response.json()["errors"][0]
        code = error.get("code", False)
        title = error.get("title", "No title?")
        body = code + ": " + title if code else title
        text = f"`[{response.status_code}] {body}`"
        await event.answer(text)


@client.onMessage(
    command=("resolve", plugin_category), outgoing=True, regex=r"resolve(?: |$)(.*)$"
)
async def resolver(event: NewMessage.Event) -> None:
    """
    Resolve an invite link or a username.


    **{prefix}resolve (invite link)**
    """
    link = event.matches[0].group(1)
    chat = None
    if not link:
        await event.answer("`Resolved the void.`")
        return
    text = f"`Couldn't resolve:` {link}"
    for link_type, pattern in invite_links.items():
        match = pattern.match(link)
        if match:
            valid = match.group(1)
            if link_type == "private":
                creatorid, cid, _ = utils.resolve_invite_link(valid)
                if not cid:
                    await event.answer(text)
                    return
                try:
                    creator = await client.get_entity(creatorid)
                    creator = await get_chat_link(creator)
                except (TypeError, ValueError):
                    creator = f"`{creatorid}`"
                text = f"**Link:** {link}"
                text += f"\n**Link creator:** {creator}\n**ID:** `{cid}`"
                try:
                    chat = await client.get_entity(cid)
                except (TypeError, ValueError):
                    break
                except Exception as e:
                    text += f"\n```{await client.get_traceback(e)}```"
                    break

                if isinstance(chat, types.Channel):
                    result = await client(
                        functions.channels.GetFullChannelRequest(channel=chat)
                    )
                    text += await misc.resolve_channel(event.client, result)
                elif isinstance(chat, types.Chat):
                    result = await client(
                        functions.messages.GetFullChatRequest(chat_id=chat)
                    )
                    text += await misc.resolve_chat(event.client, result)
                break
            else:
                try:
                    chat = await client.get_entity(valid)
                except (TypeError, ValueError):
                    continue

                if isinstance(chat, types.User):
                    text = f"**ID:** `{chat.id}`"
                    if chat.username:
                        text += f"\n**Username:** @{chat.username}"
                    text += f"\n{await get_chat_link(chat)}"

                if isinstance(chat, types.ChatForbidden):
                    text += f"\n`Not allowed to view {chat.title}.`"
                elif isinstance(chat, types.ChatEmpty):
                    text += "\n`The chat is empty.`"
                elif isinstance(chat, types.Chat):
                    text = f"**Chat:** @{valid}"
                    result = await client(
                        functions.messages.GetFullChatRequest(chat_id=chat)
                    )
                    text += await misc.resolve_chat(event.client, result)

                if isinstance(chat, types.ChannelForbidden):
                    text += f"\n`Not allowed to view {chat.title}.`"
                elif isinstance(chat, types.Channel):
                    text = f"**Channel:** @{valid}"
                    result = await client(
                        functions.channels.GetFullChannelRequest(channel=chat)
                    )
                    text += await misc.resolve_channel(event.client, result)
    await event.answer(text, link_preview=False)


@client.onMessage(command=("mention", plugin_category), outgoing=True)
async def bot_mention(event: NewMessage.Event) -> None:
    """
    Mention a user in the bot like link with a custom name.


    **Hi @kandnub[kandboob]**
    """
    newstr = event.text
    if event.entities:
        newstr = nameexp.sub(r'<a href="tg://user?id=\2">\3</a>', newstr, 0)
        for match in usernexp.finditer(newstr):
            user = match.group(1)
            text = match.group(2)
            name, entities = await client._parse_message_text(text, "md")
            rep = f'<a href="tg://resolve?domain={user}">{name}</a>'
            if entities:
                for e in entities:
                    tag = None
                    if isinstance(e, types.MessageEntityBold):
                        tag = "<b>{}</b>"
                    elif isinstance(e, types.MessageEntityItalic):
                        tag = "<i>{}</i>"
                    elif isinstance(e, types.MessageEntityCode):
                        tag = "<code>{}</code>"
                    elif isinstance(e, types.MessageEntityStrike):
                        tag = "<s>{}</s>"
                    elif isinstance(e, types.MessageEntityPre):
                        tag = "<pre>{}</pre>"
                    elif isinstance(e, types.MessageEntityUnderline):
                        tag = "<u>{}</u>"
                    if tag:
                        rep = tag.format(rep)
            newstr = re.sub(re.escape(match.group(0)), rep, newstr)
    if newstr != event.text:
        await event.answer(newstr, parse_mode="html")


@client.onMessage(
    command=("paste", plugin_category), outgoing=True, regex=r"paste(?: |$|\n)([\s\S]*)"
)
async def deldog(event: NewMessage.Event) -> None:
    """
    Paste the content to [DelDog](https://del.dog/).


    `{prefix}paste` in reply to a document/message or **{prefix}paste (text)**
    """
    match = event.matches[0].group(1)
    if match:
        text = match.strip()
    elif event.reply_to_msg_id:
        reply = await event.get_reply_message()
        if reply.document and reply.document.mime_type.startswith("text"):
            text = await reply.download_media(file=bytes)
        else:
            text = reply.raw_text
    else:
        await event.answer("`Pasted the void.`")
        return
    response = await client.loop.run_in_executor(
        None, functools.partial(dogbin_post, text)
    )
    if not response.ok:
        await event.answer(
            "Couldn't post the data to [DelDog](https://del.dog/)", reply=True
        )
        return
    key = response.json()["key"]
    await event.answer(f"`Successfully pasted on` [DelDog](https://del.dog/{key})")


@client.onMessage(command=("repo", plugin_category), outgoing=True, regex=r"repo$")
async def git_repo(event: NewMessage.Event) -> None:
    """
    Get the repo url.


    `{prefix}repo`
    """
    try:
        repo = git.Repo(".")
        remote_url = repo.remote().url.replace(".git", "/")
        if remote_url[-1] != "/":
            remote_url = remote_url + "/"
        repo.__del__()
    except Exception as e:
        LOGGER.info("Couldnt fetch the repo link.")
        LOGGER.debug(e)
        remote_url = "https://github.com/AvinashReddy3108/PaperplaneRemix.git"
    await event.answer(
        f"Click [here]({remote_url}) to check out my userbot's source code."
    )
