import asyncio
import importlib
import pkgutil
from tt.config import settings, logger
import schedule


class PluginManager:
    """🔌 Plugin Manager for dynamically loading plugins """
    def __init__(self, plugin_directory=None):
        self.plugin_directory = plugin_directory or settings.plugin_directory
        self.plugins = []

    def load_plugins(self):
        """ Load plugins from the specified directory """
        logger.info("Loading plugins from directory: %s", self.plugin_directory)
        logger.debug("Plugin directory: %s", self.plugin_directory)
        for plugin_name in pkgutil.iter_modules(path=[self.plugin_directory]):
            logger.debug("plugin_name: %s", plugin_name)
            try:
                module = importlib.import_module(f"{plugin_name}")
                logger.info("Module loaded: %s", module)
                self.load_plugin(module, plugin_name)
            except Exception as e:
                logger.warning("Error loading plugin %s: %s", plugin_name, e)

    def load_plugin(self, module, plugin_name):
        """ Load a plugin from a module """
        logger.debug("plugin_name: %s", plugin_name)
        for name, obj in module.__dict__.items():
            if (isinstance(obj, type)
                    and issubclass(obj, BasePlugin)
                    and obj is not BasePlugin):
                plugin_instance = obj()
                self.plugins.append(plugin_instance)
                logger.info("Plugin loaded: %s", plugin_name)

    async def start_all_plugins(self):
        """ Start all plugins """
        try:
            for plugin in self.plugins:
                await self.start_plugin(plugin)
        except Exception as error:
            logger.error("Error starting plugins: %s", error)
 
    async def start_plugin(self, plugin):
        """ Start a plugin """
        await plugin.start()

    async def process_message(self, message):
        """ Process message from the plugin """
        self.logger.debug("message being process by plugin %s", message)
        for plugin in self.plugins:
            if plugin.should_handle(message):
                await plugin.handle_message(message)


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

    def schedule_example(self, function):
        # Define the schedule example task
        schedule.every().day.at("10:00").do(function)

    def schedule_example_hourly(self, function):
        # Define the schedule example hourly task
        schedule.every().hour.do(function)

    def schedule_example_every_8_hours(self, function):
        # Define the schedule example every 8 hours task
        schedule.every(8).hours.do(function)

    async def run_schedule(self):
        while True:
            schedule.run_pending()
            await asyncio.sleep(10)
