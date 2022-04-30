#
# PaperplaneRemix - A modular Telegram selfbot script
# Copyright (C) 2022, Avinash Reddy and the PaperplaneRemix contributors
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import configparser
import dataclasses
import inspect
import logging
import traceback

from telethon import TelegramClient, events
from telethon.tl import types

from .custom import answer, resanswer
from .events import MessageEdited, NewMessage
from .FastTelethon import download_file, upload_file
from .parser import parse_arguments
from .pluginManager import PluginManager

LOGGER = logging.getLogger(__name__)
no_info = "There is no help available for this command!"
no_usage = "There is no usage info available for this command!"


@dataclasses.dataclass
class Command:
    func: callable
    handlers: list
    info: str
    usage: str
    builtin: bool


class UserBotClient(TelegramClient):
    """UserBot client with additional attributes inheriting TelegramClient"""

    commandcategories: dict[str, list[str]] = {}
    commands: dict[str, Command] = {}
    config: configparser.ConfigParser = None
    database: bool = True
    disabled_commands: dict[str, Command] = {}
    failed_imports: list = []
    logger: bool or types.Channel or types.User = False
    pluginManager: PluginManager = None
    plugins: list = []
    prefix: str = None
    reconnect: bool = True
    register_commands: bool = False
    running_processes: dict = {}
    version: int = 0

    def onMessage(
        self: TelegramClient,
        builtin: bool = False,
        command: str or tuple = None,
        edited: bool = True,
        info: str = None,
        doc_args: dict = {},
        **kwargs
    ) -> callable:
        """Method to register a function without the client"""

        kwargs.setdefault("forwards", False)

        def wrapper(func: callable) -> callable:
            events.register(NewMessage(**kwargs))(func)

            if edited:
                events.register(MessageEdited(**kwargs))(func)

            if self.register_commands and command:
                handlers = events._get_handlers(func)
                category = "misc"
                doc_args.setdefault("prefix", self.prefix or ".")
                if isinstance(command, tuple):
                    if len(command) == 2:
                        com, category = command
                    else:
                        raise ValueError
                else:
                    com = command
                help_doc = info or func.__doc__ or no_info
                _doc = inspect.cleandoc(help_doc).split("\n\n\n", maxsplit=1)
                if len(_doc) > 1:
                    comInfo = _doc[0].strip()
                    comUsage = _doc[1].strip()
                else:
                    comInfo = _doc[0]
                    comUsage = no_usage

                UBcommand = Command(
                    func,
                    handlers,
                    comInfo.format(**doc_args).strip(),
                    comUsage.format(**doc_args).strip(),
                    builtin,
                )
                category = category.lower()
                self.commands.update({com: UBcommand})
                self.commandcategories.setdefault(category, []).append(com)
                if builtin:
                    self.commandcategories.setdefault("builtin", []).append(com)
            return func

        return wrapper

    async def get_traceback(self, exc: Exception) -> str:
        return "".join(
            traceback.format_exception(etype=type(exc), value=exc, tb=exc.__traceback__)
        )

    def _updateconfig(self) -> bool:
        """Update the config. Sync method to avoid issues."""
        with open("config.ini", "w+") as configfile:
            self.config.write(configfile)
        return True

    def _kill_running_processes(self) -> None:
        """Kill all the running asyncio subprocessess"""
        for _, process in self.running_processes.items():
            try:
                process.kill()
                LOGGER.debug("Killed %d which was still running.", process.pid)
            except Exception as e:
                LOGGER.debug(e)
        self.running_processes.clear()


UserBotClient.fast_download_file = download_file
UserBotClient.fast_upload_file = upload_file
UserBotClient.parse_arguments = parse_arguments
UserBotClient.answer = answer
UserBotClient.resanswer = resanswer
