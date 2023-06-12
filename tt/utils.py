
import asyncio
from tt.config import settings, logger
from apprise import Apprise, NotifyFormat
from iamlistening import Listener

import importlib
import pkgutil
from typing import Dict, Optional

# async def listener(plugin_manager):
#     """Launch Listener"""
#     bot_listener = Listener()
#     task = asyncio.create_task(bot_listener.run_forever())

#     while True:
#         try:
#             msg = await bot_listener.get_latest_message()
#             if msg:
#                 # Process the message to each loaded plugin
#                 for plugin_instance in plugin_manager.plugins.values():
#                     await plugin_instance.listen(msg)
#         except Exception as error:
#             logger.error("Error in listener: %s", error)

#     await task

# async def listener(plugin_manager):
#     """Launch Listener"""
#     bot_listener = Listener()
#     task = asyncio.create_task(bot_listener.run_forever())

#     pause_event = asyncio.Event()  # Create an event for pausing/resuming the scanner

#     while True:
#         try:
#             msg = await bot_listener.get_latest_message()
#             if msg:
#                 # Process the message to each loaded plugin
#                 for plugin_instance in plugin_manager.plugins.values():
#                     await plugin_instance.listen(msg)

#                 # Check if the scanner needs to be paused or resumed
#                 if "pause scanner" in msg.lower():
#                     pause_event.clear()  # Pause the scanner
#                 elif "resume scanner" in msg.lower():
#                     pause_event.set()  # Resume the scanner
#         except Exception as error:
#             logger.error("Error in listener: %s", error)

    # await task
async def notify(msg):
    """💬 MESSAGING """
    if not msg:
        return
    apobj = Apprise()
    if settings.discord_webhook_id:
        url = (f"discord://{str(settings.discord_webhook_id)}/"
               f"{str(settings.discord_webhook_token)}")
        if isinstance(msg, str):
            msg = msg.replace("<code>", "`")
            msg = msg.replace("</code>", "`")
    elif settings.matrix_hostname:
        url = (f"matrixs://{settings.matrix_user}:{settings.matrix_pass}@"
               f"{settings.matrix_hostname[8:]}:443/"
               f"{str(settings.bot_channel_id)}")
    else:
        url = (f"tgram://{str(settings.bot_token)}/"
               f"{str(settings.bot_channel_id)}")
    try:
        apobj.add(url)
        await apobj.async_notify(body=str(msg), body_format=NotifyFormat.HTML)
    except Exception as e:
        logger.error("%s not sent: %s", msg, e)


class PluginManager:
    def __init__(self):
        self.plugins = {}

    def load_plugins(self, package_name):
        print(f"Loading plugins from package: {package_name}")
        package = importlib.import_module(package_name)
        print(f"Package loaded: {package}")
    
        for _, plugin_name, _ in pkgutil.iter_modules(package.__path__):
            try:
                module = importlib.import_module(f"{package_name}.{plugin_name}")
    
                for name, obj in module.__dict__.items():
                    if isinstance(obj, type) and issubclass(obj, BasePlugin) and obj is not BasePlugin:
                        plugin_instance = obj()
                        self.plugins[plugin_name] = plugin_instance
                        print(f"Plugin loaded: {plugin_name}")
    
            except Exception as e:
                print(f"Error loading plugin: {plugin_name}, {e}")

    async def start_plugin(self, plugin_name):
        if plugin_name in self.plugins:
            plugin_instance = self.plugins[plugin_name]
            await plugin_instance.start()
        else:
            print(f"Plugin not found: {plugin_name}")

    async def start_all_plugins(self):
        for plugin_instance in self.plugins.values():
            await plugin_instance.start()


class BasePlugin:
    def start(self):
        pass

    def stop(self):
        pass

    async def listen(self):
        pass

    async def notify(self, message):
        pass
