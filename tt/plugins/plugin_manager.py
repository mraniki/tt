import asyncio

# import httpimport
import importlib
import pkgutil

import schedule

from tt.config import logger, settings


class PluginManager:
    """🔌 Plugin Manager for loading plugins """
    def __init__(self, plugin_directory=None):
        self.plugin_directory = plugin_directory or settings.plugin_directory
        self.plugins = []

    def load_plugins(self):
        """ Load plugins from directory """
        package = importlib.import_module(self.plugin_directory)
        logger.debug("Loading plugins from: %s", package)
        for _, plugin_name, _ in pkgutil.iter_modules(package.__path__):
            try:
                module = importlib.import_module(
                    f"{self.plugin_directory}.{plugin_name}")
                logger.debug("Module loaded: %s", module)
                self.load_plugin(module, plugin_name)
            except Exception as e:
                logger.warning("Error loading plugin %s: %s", plugin_name, e)
        # if settings.user_plugins_allowed:
        #     with httpimport.github_repo('mraniki', 'tt_plugins'):
        #         import user_plugins
        #         user_package = importlib.import_module(user_plugins)
        #         logger.debug("Loading plugins from: %s", user_package)
        #         for _, plugin_name, _ in pkgutil.iter_modules(user_plugins):
        #             try:
        #                 module = importlib.import_module(
        #                     f"{user_plugins.__name__}.{plugin_name}")
        #                 logger.debug("Module loaded: %s", module)
        #                 self.load_plugin(module, plugin_name)
        #             except Exception as e:
        #                 logger.warning("Error loading user plugin %s: %s",
        # plugin_name, e)


    def load_plugin(self, module, plugin_name):
        """ Load a plugin from a module """
        logger.debug("plugin_name: %s", plugin_name)
        for name, obj in module.__dict__.items():
            if (isinstance(obj, type)
                    and issubclass(obj, BasePlugin)
                    and obj is not BasePlugin):
                plugin_instance = obj()
                self.plugins.append(plugin_instance)
                logger.debug("Plugin loaded: %s", name)

    async def start_all_plugins(self):
        """ Start all plugins """
        for plugin in self.plugins:
            await self.start_plugin(plugin)
 
    async def start_plugin(self, plugin):
        """ Start a plugin """
        await plugin.start()

    async def process_message(self, message):
        """ Send message to plugins """
        for plugin in self.plugins:
            try:
                if plugin.should_handle(message):
                    await plugin.handle_message(message)
            except Exception as error:

                logger.error("process %s: %s", plugin, error)
                continue



class BasePlugin:
    """
    ⚡ Base Plugin Class

    """
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

    def schedule_at_time(self, function):
        # Define at specific time schedule
        schedule.every().day.at("18:00").do(function)

    def schedule_hourly(self, function):
        # Define hourly schedule
        def wrapper(*args, **kwargs):
            schedule.every().hour.do(function, *args, **kwargs)
        return wrapper

    def schedule_every_8_hours(self, function):
        # Define every 8 hours schedule
        def wrapper(*args, **kwargs):
            schedule.every(8).hours.do(function, *args, **kwargs)
        return wrapper

    async def run_schedule(self):
        while True:
            schedule.run_pending()
            await asyncio.sleep(10)

    @staticmethod
    def notify_hourly(function):
        # Define hourly schedule for sending notifications
        def wrapper(self):
            self.schedule_hourly(self.send_notification(function))
        return wrapper