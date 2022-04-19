#
# PaperplaneRemix - A modular Telegram selfbot script
# Copyright (C) 2022, Avinash Reddy and the PaperplaneRemix contributors
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import asyncio
import concurrent
import functools
import os
import pathlib
import re
import time
import yt_dlp

from .. import LOGGER

downloads = {}
audio = re.compile(r"\[ExtractAudio\] Destination\: (.+)")
video = re.compile(
    r"\[VideoConvertor\] Converting video from \w+ to \w+; Destination: (.+)"
)
merger = re.compile(r'\[Merger\] Merging formats into "(.+)"')


class YTdlLogger(object):
    """Logger used for YoutubeDL which logs to UserBot logger."""

    def debug(self, msg: str) -> None:
        """Logs debug messages with yt-dlp tag to UserBot logger."""
        LOGGER.debug("yt-dlp: " + msg)
        f = None
        if audio.search(msg):
            f = audio.match(msg).group(1)
        if video.search(msg):
            f = video.match(msg).group(1)
        if merger.search(msg):
            f = merger.match(msg).group(1)
        if f:
            downloads.update({f.split(".")[0]: f})

    def warning(self, msg: str) -> None:
        """Logs warning messages with yt-dlp tag to UserBot logger."""
        LOGGER.warning("yt-dlp: " + msg)

    def error(self, msg: str) -> None:
        """Logs error messages with yt-dlp tag to UserBot logger."""
        LOGGER.error("yt-dlp: " + msg)

    def critical(self, msg: str) -> None:
        """Logs critical messages with yt-dlp tag to UserBot logger."""
        LOGGER.critical("yt-dlp: " + msg)


class ProgressHook:
    """Custom hook with the event stored for YTDL."""

    def __init__(self, event, update=5):
        self.loop = asyncio.get_event_loop()
        self.event = event
        self.downloaded = 0
        self.tasks = []
        self.update = update
        self.last_edit = None

    def callback(self, task):
        """Cancel pending tasks else skip them if completed."""
        if task.cancelled():
            return
        new = task.result().date
        if new > self.last_edit:
            self.last_edit = new

    def edit(self, *args, **kwargs):
        """Create a Task of the progress edit."""
        task = self.loop.create_task(self.event.answer(*args, **kwargs))
        self.tasks.append(task)
        return task

    def hook(self, d: dict) -> None:
        """
        YoutubeDL's hook which logs progress and errors to UserBot logger.
        """
        if d["status"] == "downloading":
            filen = d.get("filename", "Unknown filename")
            prcnt = d.get("_percent_str", None)
            ttlbyt = d.get("_total_bytes_str", None)
            spdstr = d.get("_speed_str", None)
            etastr = d.get("_eta_str", None)

            if not prcnt or not ttlbyt or not spdstr or not etastr:
                return

            finalStr = "Downloading {}: {} of {} at {} ETA: {}".format(
                filen, prcnt, ttlbyt, spdstr, etastr
            )
            LOGGER.debug(finalStr)
            if float(prcnt[:-1]) - self.downloaded >= self.update:
                # Avoid spamming recents
                if self.last_edit and time.time() - self.last_edit < 10:
                    return
                self.downloaded = float(prcnt[:-1])
                filen = re.sub(r"YT_DL\\(.+)_\d+\.", r"\1.", filen)
                self.edit(
                    f"`Downloading {filen} at {spdstr}.`\n"
                    f"__Progress: {prcnt} of {ttlbyt}__\n"
                    f"__ETA: {etastr}__"
                )
                self.last_edit = time.time()

        elif d["status"] == "finished":
            filen = d.get("filename", "Unknown filename")
            filen1 = re.sub(r"YT_DL\\(.+)_\d+\.", r"\1.", filen)
            ttlbyt = d.get("_total_bytes_str", None)
            elpstr = d.get("_elapsed_str", None)
            downloads.update({filen.split(".")[0]: filen})

            if not ttlbyt or not elpstr:
                return

            finalStr = f"Downloaded {filen}: 100% of {ttlbyt} in {elpstr}"
            LOGGER.warning(finalStr)
            self.loop.create_task(
                self.event.answer(f"`Successfully downloaded {filen1} in {elpstr}!`")
            )
            for task in self.tasks:
                if not task.done():
                    task.cancel()
            self.tasks.clear()

        elif d["status"] == "error":
            finalStr = "Error: " + str(d)
            LOGGER.error(finalStr)


# https://stackoverflow.com/a/68165682
# https://gist.github.com/jmilldotdev/b107f858729064daa940057fc9b14e89
class FilenameCollectorPP(yt_dlp.postprocessor.common.PostProcessor):
    def __init__(self):
        super(FilenameCollectorPP, self).__init__(None)
        self.filenames = []

    def run(self, information):
        self.filenames.append(information["filepath"])
        return [], information


async def list_formats(info_dict: dict) -> str:
    """YoutubeDL's list_formats method but without format notes.

    Args:
        info_dict (``dict``):
            Dictionary which is returned by YoutubeDL's extract_info method.

    Returns:
        ``str``:
            All available formats in order as a string instead of stdout.
    """
    formats = info_dict.get("formats", [info_dict])
    table = [
        [f["format_id"], f["ext"], yt_dlp.YoutubeDL.format_resolution(f)]
        for f in formats
        if f.get("preference") is None or f["preference"] >= -1000
    ]
    if len(formats) > 1:
        table[-1][-1] += (" " if table[-1][-1] else "") + "(best)"

    header_line = ["format code", "extension", "resolution"]
    return "Available formats for %s:\n%s" % (
        info_dict["title"],
        yt_dlp.render_table(header_line, table),
    )


async def extract_info(
    loop,
    executor: concurrent.futures.Executor,
    ydl_opts: dict,
    url: str,
    download: bool = False,
) -> str:
    """Runs YoutubeDL's extract_info method without blocking the event loop.

    Args:
        executor (:obj:`concurrent.futures.Executor <concurrent.futures>`):
            Either ``ThreadPoolExecutor`` or ``ProcessPoolExecutor``.
        params (``dict``):
            Parameters/Keyword arguments to use for YoutubeDL.
        url (``str``):
            The url which you want to use for extracting info.
        download (``bool``, optional):
            If you want to download the video. Defaults to False.

    Returns:
        ``str``:
            Successfull string or info_dict on success or an exception's
            string if any occur.
    """
    ydl_opts["outtmpl"] = ydl_opts["outtmpl"].format(time=time.time_ns())
    ytdl = yt_dlp.YoutubeDL(ydl_opts)
    filename_collector = FilenameCollectorPP()
    ytdl.add_post_processor(filename_collector)

    def downloader(url, download):
        eStr = None
        try:
            info = ytdl.extract_info(url, download=download)
            info_dict = ytdl.sanitize_info(info)
        except yt_dlp.utils.DownloadError as DE:
            eStr = f"`{DE}`"
        except yt_dlp.utils.ContentTooShortError:
            eStr = "`There download content was too short.`"
        except yt_dlp.utils.GeoRestrictedError:
            eStr = (
                "`Video is not available from your geographic location due "
                "to geographic restrictions imposed by a website.`"
            )
        except yt_dlp.utils.MaxDownloadsReached:
            eStr = "`Max-downloads limit has been reached.`"
        except yt_dlp.utils.PostProcessingError:
            eStr = "`There was an error during post processing.`"
        except yt_dlp.utils.UnavailableVideoError:
            eStr = "`Video is not available in the requested format.`"
        except yt_dlp.utils.XAttrMetadataError as XAME:
            eStr = f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`"
        except yt_dlp.utils.ExtractorError:
            eStr = "`There was an error during info extraction.`"
        except Exception as e:
            return e
        if eStr:
            return eStr

        if not download:
            return info_dict

        filen = filename_collector.filenames[0]
        opath = downloads.pop(filen.rsplit(".", maxsplit=1)[0], filen)
        downloaded = pathlib.Path(opath)
        if not downloaded.exists():
            pattern = f"*{info_dict['title']}*"
            for f in pathlib.Path(downloaded.parent).glob(pattern):
                if f.suffix != ".jpg":
                    opath = f"YT_DL/{f.name}{f.suffix}"
                    break
        npath = re.sub(r"_\d+(\.\w+)$", r"\1", opath)
        thumb = pathlib.Path(re.sub(r"\.\w+$", r".jpg", opath))

        old_f = pathlib.Path(npath)
        new_f = pathlib.Path(opath)
        if old_f.exists():
            if old_f.samefile(new_f):
                os.remove(str(new_f.absolute()))
            else:
                newname = str(old_f.stem) + "_OLD"
                old_f.replace(old_f.with_name(newname).with_suffix(old_f.suffix))
        path = new_f.parent.parent / npath
        new_f.rename(new_f.parent.parent / npath)
        thumb = str(thumb.absolute()) if thumb.exists() else None
        return path.absolute(), thumb, info_dict

    # Future blocks the running event loop
    # fut = executor.submit(downloader, url, download)
    # result = fut.result()
    result = None
    try:
        result = await loop.run_in_executor(
            concurrent.futures.ThreadPoolExecutor(),
            functools.partial(downloader, url, download),
        )
    except Exception as e:
        result = f"```{type(e)}: {e}```"
    finally:
        return result
