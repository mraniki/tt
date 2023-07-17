"""
 talky Utils
"""
__version__ = "4.0.0"

import asyncio
from apprise import Apprise, NotifyFormat
from tt.config import settings, logger
from tt.plugins.plugin_manager import PluginManager
from iamlistening import Listener


async def send_notification(msg):
    """
    💬 Notification via Apprise 
    """
    aobj = Apprise()
    if settings.apprise_api_endpoint:
        aobj.add(settings.apprise_api_endpoint)
    elif settings.apprise_config:
        aobj.add(settings.apprise_config)
    elif settings.apprise_url:
        aobj.add(settings.apprise_url)
    await aobj.async_notify(body=msg, body_format=NotifyFormat.HTML)


async def start_listener(max_iterations=None):
    """
    Start the chat listener.
    """
    bot_listener = Listener()
    task = asyncio.create_task(bot_listener.run_forever(max_iterations))
    return bot_listener, task


async def start_plugins(plugin_manager):
    """
    Start all plugins.
    """
    if settings.plugin_enabled:
        plugin_manager.load_plugins()
        loop = asyncio.get_running_loop()
        loop.create_task(plugin_manager.start_all_plugins())

async def start_bot(listener, plugin_manager):
    """
    Listen to the message in the bot channel
    and dispatch to plugins
    """
    while True:
        try:
            msg = await listener.get_latest_message()
            if msg and settings.plugin_enabled:
                await plugin_manager.process_message(msg)
        except Exception as error:
            logger.error("👂 listener: %s", error)

        await asyncio.sleep(1)


async def run_bot(max_iterations=None):
    """
    Run the chat bot & the plugins.
    """
    listener, task = await start_listener(max_iterations)
    plugin_manager = PluginManager()
    await start_plugins(plugin_manager)
    await asyncio.gather(start_bot(listener, plugin_manager), task)