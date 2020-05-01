# TG-UserBot - A modular Telegram UserBot script for Python.
# Copyright (C) 2019  Kandarp <https://github.com/kandnub>
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

import configparser
import logging
import pathlib
import platform
import sys

import redis
from telethon.tl import types

from sessions.redis import RedisSession
from .utils.config_helper import resolve_env
from .utils.client import UserBotClient

__version__ = "0.5"
__license__ = "GNU General Public License v3.0"
__author__ = 'Kandarp <https://github.com/kandnub>'
__copyright__ = (
    "TG-UserBot  Copyright (C) 2019  Kandarp <https://github.com/kandnub>")
LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

root = pathlib.Path(__file__).parent.parent

session = "userbot"
redis_db = False
loop = None
config = configparser.ConfigParser()
config_file = pathlib.Path(root / 'config.ini')
sql_session = pathlib.Path(root / 'userbot.session')

ROOT_LOGGER = logging.getLogger()
LOGGER = logging.getLogger(__name__)

if sys.platform.startswith('win'):
    from asyncio import ProactorEventLoop
    from os import system

    loop = ProactorEventLoop()
    system('color')

if platform.python_version_tuple() < ('3', '7', '3'):
    print("Please run this script with Python 3.7.3 or above."
          "\nExiting the script.")
    sys.exit(1)

if config_file.exists():
    config.read(config_file)
    resolve_env(config)

try:
    resolve_env(config)
except ValueError:
    print("Please make sure you have a proper config.ini in this directory "
          "or the required environment variables set."
          "\nExiting the script.")
    sys.exit(1)

if "telethon" not in config:
    print("You're not using a valid config, refer to the sample_config.ini")
    sys.exit(1)

telethon = config['telethon']
API_ID = telethon.getint('api_id', False)
API_HASH = telethon.get('api_hash', False)

database = config['database']
REDIS_ENDPOINT = database.get('redis_endpoint', False)
REDIS_PASSWORD = database.get('redis_password', False)

userbot = config['userbot']
LOGGER_CHAT_ID = userbot.getint('logger_group_id', 0)
CONSOLE_LOGGER = userbot.get('console_logger_level', 'INFO')

if CONSOLE_LOGGER.upper() in LEVELS:
    level = LEVELS[CONSOLE_LOGGER.upper()]
    ROOT_LOGGER.setLevel(level)
    LOGGER.setLevel(level)

if not (API_ID and API_HASH):
    print("You need to set your API keys in your config or environment!")
    LOGGER.debug("No API keys!")
    sys.exit(1)

if REDIS_ENDPOINT and REDIS_PASSWORD:
    REDIS_HOST = REDIS_ENDPOINT.split(':')[0]
    REDIS_PORT = REDIS_ENDPOINT.split(':')[1]
    redis_connection = redis.Redis(host=REDIS_HOST,
                                   port=REDIS_PORT,
                                   password=REDIS_PASSWORD)
    try:
        redis_connection.ping()
    except Exception as e:
        LOGGER.exception(e)
        print()
        LOGGER.error(
            "Make sure you have the correct Redis endpoint and password "
            "and your machine can make connections.")
        sys.exit(1)
    LOGGER.debug("Connected to Redis successfully!")
    redis_db = redis_connection
    if not sql_session.exists():
        LOGGER.debug("Using Redis session!")
        session = RedisSession("userbot", redis_connection)

client = UserBotClient(session=session,
                       api_id=API_ID,
                       api_hash=API_HASH,
                       loop=loop,
                       app_version=__version__,
                       auto_reconnect=False)

client.version = __version__
client.config = config
client.prefix = userbot.get('userbot_prefix', None)
client.database = redis_db


def verifyLoggerGroup(client: UserBotClient) -> None:
    client.logger = True

    def disable_logger(error: str):
        if LOGGER_CHAT_ID != 0:
            LOGGER.error(error)
        client.logger = False

    try:
        entity = client.loop.run_until_complete(
            client.get_entity(LOGGER_CHAT_ID))
        if not isinstance(entity, types.User):
            if not entity.creator:
                if entity.default_banned_rights.send_messages:
                    disable_logger("Permissions missing to send messages "
                                   "for the specified Logger group.")
    except ValueError:
        disable_logger("Logger group ID cannot be found. "
                       "Make sure it's correct.")
    except TypeError:
        disable_logger("Logger group ID is unsupported. "
                       "Make sure it's correct.")
    except Exception as e:
        disable_logger("An Exception occured upon trying to verify "
                       "the logger group.\n" + str(e))
