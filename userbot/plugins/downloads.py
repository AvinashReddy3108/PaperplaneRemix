#
# PaperplaneRemix - A modular Telegram selfbot script
# Copyright (C) 2022, Avinash Reddy and the PaperplaneRemix contributors
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import io
import pathlib

from telethon.tl import types
from telethon.utils import get_attributes, get_extension

from userbot import client
from userbot.utils.events import NewMessage
from userbot.utils.helpers import ProgressCallback

plugin_category = "downloads"
downloads = pathlib.Path("./downloads/").absolute()
NAME = "untitled"


async def _get_file_name(path: pathlib.Path, full: bool = True) -> str:
    return str(path.absolute()) if full else path.stem + path.suffix


@client.onMessage(
    command=("download", plugin_category),
    outgoing=True,
    regex=r"d(own)?l(oad)?(?: |$)(.+)?$",
)
async def download(event: NewMessage.Event) -> None:
    """
    Download documents from Telegram.


    `{prefix}download` or `{prefix}dl` or **{prefix}download (path)**
    """
    name = NAME
    path = None
    match = event.matches[0].group(3)
    if match:
        path = pathlib.Path(match.strip())

    if not event.reply_to_msg_id:
        await event.answer("`Downloaded the void.`")
        return

    reply = await event.get_reply_message()
    if not (reply.document or reply.media):
        await event.answer("`There is no document/media in here to download!`")
        return

    for attr in getattr(reply.document, "attributes", []):
        if isinstance(attr, types.DocumentAttributeFilename):
            name = attr.file_name
    ext = get_extension(reply.document)
    if path and not path.suffix and ext:
        path = path.with_suffix(ext)
    if name == NAME:
        name += "_" + str(getattr(reply.document, "id", reply.id)) + ext

    if path and path.exists():
        if path.is_file():
            newname = str(path.stem) + "_OLD"
            path.rename(path.with_name(newname).with_suffix(path.suffix))
            file_name = path
        else:
            file_name = path / name
    elif path and not path.suffix and ext:
        file_name = downloads / path.with_suffix(ext)
    elif path:
        file_name = path
    else:
        file_name = downloads / name
    file_name.parent.mkdir(parents=True, exist_ok=True)

    prog = ProgressCallback(event, filen=await _get_file_name(file_name, False))
    if reply.document:
        dl = io.FileIO(file_name.absolute(), "a")
        await client.fast_download_file(
            location=reply.document, out=dl, progress_callback=prog.dl_progress
        )
        dl.close()
    else:
        await reply.download_media(
            file=file_name.absolute(), progress_callback=prog.dl_progress
        )

    await event.answer(
        f"__Downloaded successfully!__\n"
        f"**Path:** `{await _get_file_name(file_name)}`"
    )


@client.onMessage(
    command=("upload", plugin_category),
    outgoing=True,
    regex=r"u(p)?l(oad)?(?: |$)(.+)?$",
)
async def upload(event: NewMessage.Event) -> None:
    """
    Upload media to Telegram.


    **{prefix}upload (path)** or **{prefix}ul (path)**
    """
    match = event.matches[0].group(3)
    target_files = []
    if not match:
        await event.answer("`Uploaded the void.`")
        return

    match = match.strip().replace("\\", "/") if match else ""
    fmatch = pathlib.Path(match)
    dmatch = pathlib.Path(downloads / match)

    if "*" not in match:
        if fmatch.exists():
            target_files.append(fmatch)
        elif dmatch.exists():
            target_files.append(dmatch)
    if not target_files:
        for f in downloads.glob("*.*"):
            if f.match(match) and f.is_file():
                target_files.append(f)
    # Un-comment this for recursive file fetching from the bot's root dir
    """for f in pathlib.Path('.').glob('**/*.*'):
        if f in target_files:
            continue
        if not f.match('*/__pycache__/*') and f.match(match) and f.is_file():
            target_files.append(f)"""

    if not target_files:
        await event.answer("`Couldn't find what you were looking for.`")
        return

    files = "\n".join(f"`{await _get_file_name(f)}`" for f in target_files)
    if len(target_files) > 1:
        await event.answer(f"**Found multiple files for {match}:**\n{files}")
        return

    for f in target_files:
        f = f.absolute()
        prog = ProgressCallback(event, filen=await _get_file_name(f, False))
        attributes, mime_type = get_attributes(str(f))
        ul = io.open(f, "rb")
        uploaded = await client.fast_upload_file(
            file=ul, progress_callback=prog.up_progress
        )
        ul.close()
        media = types.InputMediaUploadedDocument(
            file=uploaded, mime_type=mime_type, attributes=attributes, thumb=None
        )
        await client.send_file(
            event.chat_id, file=media, force_document=True, reply_to=event
        )

    await event.answer(f"`Successfully uploaded {files}.`")
