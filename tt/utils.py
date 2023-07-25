"""
 talky Utils
"""
__version__ = "4.5.0"


import asyncio

from apprise import Apprise, NotifyFormat
from iamlistening import Listener

from tt.config import settings
from tt.plugins.plugin_manager import PluginManager


async def send_notification(msg):
    """
    💬 Notification via Apprise 
    """
    aobj = Apprise(settings.apprise_url)
    msg_format = settings.apprise_format or NotifyFormat.MARKDOWN
    await aobj.async_notify(
        body=msg,
        body_format=msg_format)


async def run_bot(max_iterations=None):
    """
    🤖 Run the chat bot & the plugins.
    """
    listener = Listener()
    plugin_manager = PluginManager()
    await asyncio.gather(start_bot(listener, plugin_manager))


async def start_plugins(plugin_manager):
    """
    🔌 Start all plugins.
    """
    if settings.plugin_enabled:
        plugin_manager.load_plugins()
        loop = asyncio.get_running_loop()
        loop.create_task(plugin_manager.start_all_plugins())

 
async def start_bot(listener, plugin_manager):
    """
    👂 Start the chat listener and dispatch to plugins
    """
    await listener.start()
    await start_plugins(plugin_manager)
    while True:
        msg = await listener.handler.get_latest_message()
        if msg and settings.plugin_enabled:
            await plugin_manager.process_message(msg)

    await asyncio.sleep(1)
