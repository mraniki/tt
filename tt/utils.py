"""
 talky Utils
"""
__version__ = "4.11.5"


import asyncio

from apprise import Apprise, NotifyFormat
from iamlistening import Listener

from tt.config import logger, settings
from tt.plugins.plugin_manager import PluginManager


async def send_notification(msg):
    """
    💬 Notification via Apprise.
    Apprise endpoint URL can be a URL 
    for the chat, a URL to an Apprise config
    or a URL to the Apprise API endpoint
    apprise_url = "tgram://BOTTOKEN/CHANNEL"
    apprise_url = "discord://token1/channel"

    Args:
        msg (str): Message

    Returns:
        None

    More info
    https://github.com/caronc/apprise/wiki

    """
    aobj = Apprise(settings.apprise_url)
    msg_format = settings.apprise_format or NotifyFormat.MARKDOWN
    try:
        await aobj.async_notify(
            body=msg,
            body_format=msg_format)
    except Exception as error:
        logger.error("Verify Apprise URL: ", error)

async def run_bot():
    """
    🤖 Run the chat bot & the plugins
    via an asyncio loop.

    Returns:
        None

    More info: https://github.com/mraniki/iamlistening

    """
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
        plugin_manager.load_plugins()
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
    await listener.start()
    await start_plugins(plugin_manager)
    iteration = 0
    while True:
        msg = await listener.handler.get_latest_message()
        if msg and settings.plugin_enabled:
            await plugin_manager.process_message(msg)
        iteration += 1
        if max_iterations is not None and iteration >= max_iterations:
            break

    await asyncio.sleep(1)
