"""
 talky Utils
"""
__version__ = "3.11.3"

import asyncio
from apprise import Apprise, NotifyFormat
from iamlistening import Listener
from tt.config import settings, logger
from tt.plugins.plugin_manager import PluginManager

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


async def listener():
    """
    👂 Chat Listener via iamlistening 
    """
    bot_listener = Listener()
    task = asyncio.create_task(bot_listener.run_forever())
    if settings.plugin_enabled:
        plugin_manager = PluginManager()
        plugin_manager.load_plugins()
        loop = asyncio.get_running_loop()
        loop.create_task(plugin_manager.start_all_plugins())

    while True:
        try:
            msg = await bot_listener.get_latest_message()
            print(msg)
            if msg:
                if settings.plugin_enabled:
                    for plugin in plugin_manager.plugins:
                        try:
                            await plugin.process_message(msg)
                        except Exception as plugin_error:
                            logger.error(
                                "Error processing message with plugin %s: %s",
                                plugin,
                                plugin_error)
        except Exception as error:
            logger.error("👂 listener: %s", error)
    await task
