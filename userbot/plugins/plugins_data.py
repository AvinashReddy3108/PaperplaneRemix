#
# PaperplaneRemix - A modular Telegram selfbot script
# Copyright (C) 2022, Avinash Reddy and the PaperplaneRemix contributors
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import base64
import dataclasses
import dill
import os


def load_data(name: str) -> dict:
    b64 = os.environ.pop(name, {})
    if b64:
        b64 = dill.loads(base64.b64decode(b64.encode()))
    return b64


def dump_data(instance) -> dict:
    data_dict = {}
    for i in dataclasses.fields(instance):
        attr = getattr(instance, i.name, None)
        if attr:
            data_dict[i.name] = base64.b64encode(dill.dumps(attr)).decode()
    return data_dict


@dataclasses.dataclass
class AFK:
    privates: dict = None
    groups: dict = None
    sent: dict = None


def dump_AFK() -> None:
    cls_dict = dump_data(AFK)
    if "privates" in cls_dict:
        os.environ["userbot_afk_privates"] = cls_dict["privates"]
    if "groups" in cls_dict:
        os.environ["userbot_afk_groups"] = cls_dict["groups"]
    if "sent" in cls_dict:
        os.environ["userbot_afk_sent"] = cls_dict["sent"]


@dataclasses.dataclass
class Blacklist:
    bio: list = None
    url: list = None
    tgid: list = None
    txt: list = None


@dataclasses.dataclass
class GlobalBlacklist:
    bio: list = None
    url: list = None
    tgid: list = None
    txt: list = None
