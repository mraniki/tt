"""
 talky Utils
"""
__version__ = "3.11.3"

import asyncio
import importlib
import pkgutil
import schedule
from tt.config import settings, logger


class PluginManager:
    """🔌 Plugin Manager for dynamically loading plugins """
    def __init__(self):
        self.plugin_directory = settings.plugin_directory
        self.plugins = []

    def load_plugins(self):
        """ Load plugins from the specified directory """
        logger.info("Loading plugins from directory: %s", self.plugin_directory)

        for _, plugin_name, _ in pkgutil.iter_modules([self.plugin_directory]):
            try:
                module = importlib.import_module(f"{plugin_name}")
                logger.info("Module loaded: %s", module)

                for name, obj in module.__dict__.items():
                    if (isinstance(obj, type)
                            and issubclass(obj, BasePlugin)
                            and obj is not BasePlugin):
                        plugin_instance = obj()
                        self.plugins.append(plugin_instance)
                        logger.info("Plugin loaded: %s", plugin_name)

            except Exception as e:
                logger.warning("Error loading plugin %s: %s", plugin_name, e)
        
        self.plugins = self.plugins

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
 
class ScheduleManager:
    """
        ⚡ Base Schedule Manager
    if a plugin need to be scheduled
    you can use the following code
    refer to example_plugin.py
    """
    def __init__(self, plugin):
        self.plugin = plugin


    def schedule_example(self,function):
        # Define the schedule example task
        schedule.every().day.at("10:00").do(function)

    def schedule_example_hourly(self,function):
        # Define the schedule example hourly task
        schedule.every().hour.do(function)

    def schedule_example_every_8_hours(self,function):
        # Define the schedule example every 8 hours task
        schedule.every(8).hours.do(function)

    async def run_schedule(self):
        while True:
            schedule.run_pending()
            await asyncio.sleep(10)
