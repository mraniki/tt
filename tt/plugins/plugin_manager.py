import asyncio

# import httpimport
import importlib
import pkgutil

import schedule

from tt.config import logger, settings


class PluginManager:
    """🔌 Plugin Manager """
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
                logger.info("Plugin loaded: %s", name)

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
    def __init__(self):
        self.has_scheduled_jobs = False

    async def start(self):
        # Start the scheduling loop as a separate task if there are scheduled jobs
        if self.has_scheduled_jobs:
            asyncio.create_task(self.run_schedule())

    async def stop(self):
        pass

    async def send_notification(self, message):
        pass

    def should_handle(self, message):
        pass

    async def handle_message(self, msg):
        pass

    def schedule_hourly(self, function):
        # Define hourly schedule
        def wrapper(*args, **kwargs):
            schedule.every().hour.do(function, *args, **kwargs)
        self.has_scheduled_jobs = True
        return wrapper

    def schedule_daily(self, function, time_str):
        # Define daily schedule at a given time
        def wrapper(*args, **kwargs):
            schedule.every().day.at(time_str).do(function, *args, **kwargs)
        self.has_scheduled_jobs = True
        return wrapper

    async def run_schedule(self):
        while self.has_scheduled_jobs:
            schedule.run_pending()
            await asyncio.sleep(10)

    @staticmethod
    def notify_hourly(function):
        # Define hourly schedule for sending notifications
        def wrapper(self):
            self.schedule_hourly(self.send_notification(function))
        return wrapper

    @staticmethod
    def notify_daily(time_str):
        # Define daily schedule for sending notifications at a given time
        def decorator(function):
            def wrapper(self):
                self.schedule_daily(self.send_notification(function), time_str)
            return wrapper
            return decorator