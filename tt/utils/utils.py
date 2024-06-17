"""
 Talky Utils

 This module contains utility functions
 for the TalkyTrader app such as:

 - send_notification
 - run_bot
 - start plugins
 - start_bot

"""

import asyncio

from iamlistening import Listener

from tt.config import logger, settings
from tt.plugins.plugin_manager import PluginManager
from tt.utils.version import check_version

# async def send_notification(msg):
#     """
#     💬 Notification via Apprise.
#     Apprise endpoint URL can be a URL
#     for the chat, an URL to an Apprise config
#     or a URL to the Apprise API endpoint
#     apprise_url = "tgram://BOTTOKEN/CHANNEL"
#     apprise_url = "discord://token1/channel"

#     Args:
#         msg (str): Message

#     Returns:
#         None

#     More info
#     https://github.com/caronc/apprise/wiki

#     """
#     notifier = Notifier()
#     await notifier.notify(msg)


async def run_bot():
    """
    🤖 Run the chat bot & the plugins
    via an asyncio loop.

    Returns:
        None

    More info: https://github.com/mraniki/iamlistening

    """
    if settings.version_check:
        await check_version()
    listener = Listener()
    plugin_manager = PluginManager()
    await asyncio.gather(start_bot(listener, plugin_manager))


async def start_plugins(plugin_manager):
    """
    🔌 Start all plugins.


    Returns:
        None

    Refer to chat manager for plugin info

    """
    if settings.plugin_enabled:
        plugin_manager.load_plugins(settings.authorized_plugins)
        loop = asyncio.get_running_loop()
        loop.create_task(plugin_manager.start_all_plugins())


async def start_bot(listener, plugin_manager, max_iterations=None):
    """
    👂 Start the chat listener and
    dispatch messages to plugins

    Args:
        listener (Listener): Listener
        plugin_manager (PluginManager): PluginManager
        max_iterations (int): Max iterations

    Returns:
        None

    """

    loop = asyncio.get_running_loop()
    loop.create_task(listener.start())
    await start_plugins(plugin_manager)
    iteration = 0
    if not listener.clients:
        logger.warning(
            """
            No listener clients.
            Verify settings and check wiki for example
            https://talky.readthedocs.io/en/latest/02_config.html
            """
        )
        return
    while True:
        for client in listener.clients:
            msg = await client.get_latest_message()
            if msg:
                await plugin_manager.process_message(msg)
        iteration += 1
        if max_iterations is not None and iteration >= max_iterations:
            break

    await asyncio.sleep(1)
