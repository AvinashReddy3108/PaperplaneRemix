#
# PaperplaneRemix - A modular Telegram selfbot script
# Copyright (C) 2022, Avinash Reddy and the PaperplaneRemix contributors
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import logging
import sys

from telethon import functions
from telethon.errors import AuthKeyError, InvalidBufferError

import userbot
from userbot import client

from .utils import helpers, pluginManager

LOGGER = logging.getLogger("userbot")
print(userbot.__copyright__)
print("Licensed under the terms of the " + userbot.__license__)


def wakeup():
    client.loop.call_later(0.1, wakeup)


if __name__ == "__main__":
    client.register_commands = True
    client.pluginManager = pluginManager.PluginManager(client)
    client.pluginManager.import_all()
    client.pluginManager.add_handlers()

    try:
        client.loop.run_until_complete(client.connect())
        config = client.loop.run_until_complete(
            client(functions.help.GetConfigRequest())
        )
        for option in config.dc_options:
            if option.ip_address == client.session.server_address:
                if client.session.dc_id != option.id:
                    LOGGER.warning(
                        f"Fixed DC ID in session from {client.session.dc_id}"
                        f" to {option.id}"
                    )
                client.session.set_dc(option.id, option.ip_address, option.port)
                client.session.save()
                break
        client.start()
    except (AuthKeyError, InvalidBufferError):
        client.session.delete()
        LOGGER.error(
            "Your old session was invalid and has been automatically deleted! "
            "Run the script again to generate a new session."
        )
        sys.exit(1)

    userbot.verifyLoggerGroup(client)
    helpers.printUser(client.loop.run_until_complete(client.get_me()))
    helpers.printVersion(client.version, client.prefix)
    client.loop.create_task(helpers.isRestart(client))

    try:
        if sys.platform.startswith("win"):
            client.loop.call_later(0.1, wakeup)  # Needed for SIGINT handling
        client.loop.run_until_complete(client.disconnected)
        if client.reconnect:
            LOGGER.info("Client was disconnected, restarting the script.")
            helpers.restarter(client)
    except NotImplementedError:
        pass
    except KeyboardInterrupt:
        print()
        LOGGER.info("Exiting the script due to keyboard interruption.")
        client._kill_running_processes()
    finally:
        client.disconnect()
