__version__ = "3.7.7"

import asyncio
import importlib
import pkgutil
from apprise import Apprise, NotifyFormat
from iamlistening import Listener
from tt.config import settings, logger


async def send_notification(msg):
    """💬 Notification via Apprise """
    aobj = Apprise()
    if settings.apprise_api_endpoint:
        aobj.add(settings.apprise_api_endpoint)
    elif settings.apprise_config:
        aobj.add(settings.apprise_config)
    elif settings.apprise_url:
        aobj.add(settings.apprise_url)
    await aobj.async_notify(body=msg, body_format=NotifyFormat.HTML)


async def listener():
    """👂 Launch Listener"""
    bot_listener = Listener()
    task = asyncio.create_task(bot_listener.run_forever())
    message_processor = MessageProcessor()
    if settings.plugin_enabled:
        message_processor.load_plugins("tt.plugins")
        loop = asyncio.get_running_loop()
        loop.create_task(start_plugins(message_processor))

    while True:
        try:
            msg = await bot_listener.get_latest_message()
            if msg:
                if settings.plugin_enabled:
                    await message_processor.process_message(msg)
        except Exception as error:
            logger.error("listener: %s", error)
    await task


async def start_plugins(message_processor):
    try:
        await message_processor.start_all_plugins()
    except Exception as error:
        logger.error("plugins start: %s", error)


class MessageProcessor:
    """👂 Message Processor for plugin """
    def __init__(self):
        self.plugins = []
        self.plugin_tasks = []

    def load_plugins(self, package_name):
        """ Load plugins from package """
        logger.info("Loading plugins from package: %s", package_name)
        package = importlib.import_module(package_name)
        logger.info("Package loaded: %s", package)

        for _, plugin_name, _ in pkgutil.iter_modules(package.__path__):
            try:
                module = importlib.import_module(f"{package_name}.{plugin_name}")
                logger.info("Module loaded: %s", module)

                for name, obj in module.__dict__.items():
                    if isinstance(obj, type) and issubclass(obj, BasePlugin) and obj is not BasePlugin:
                        plugin_instance = obj()
                        self.plugins.append(plugin_instance)
                        logger.info("Plugin loaded: %s", plugin_name)

            except Exception as e:
                logger.warning("Error loading plugin %s: %s", plugin_name, e)

    async def start_plugin(self, plugin_name):
        """ Start plugin """
        if plugin_name in self.plugins:
            plugin_instance = self.plugins[plugin_name]
            await plugin_instance.start()
        else:
            logger.warning("Plugin not found:  %s", plugin_name)

    async def start_all_plugins(self):
        """ Start all plugins """
        try:
            for plugin in self.plugins:
                task = asyncio.create_task(plugin.start())
                self.plugin_tasks.append(task)
            await asyncio.gather(*self.plugin_tasks)
        except Exception as e:
            logger.warning("error starting all plugins %s", e)

    async def process_message(self, message):
        """ Process message from the plugin """
        plugin_dict = {plugin.name: plugin for plugin in self.plugins}
        # replies = []
        for plugin in plugin_dict.values():
            if plugin.should_handle(message):
                await plugin.handle_message(message)
                # reply = await plugin.handle_message(message)
                # if reply:
                #     replies.append(reply)
            # consolidated_reply = '\n'.join(replies)  # Combine the replies into a single string
            # if consolidated_reply:
            #     await send_notification(consolidated_reply)


class BasePlugin:
    """⚡ Base Plugin"""
    async def start(self):
        pass
    async def stop(self):
        pass
    async def send_notification(self, message):
        pass
    def should_handle(self, message):
        pass
    async def handle_message(self, msg):
        pass
