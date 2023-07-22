
import importlib
import pkgutil

from asyncz.schedulers.asyncio import AsyncIOScheduler

from tt.config import logger, settings


class PluginManager:
    """🔌 Plugin Manager """
    def __init__(self, plugin_directory=None):
        self.plugin_directory = plugin_directory or settings.plugin_directory
        self.plugins = []
        self.scheduler = None

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
        self.scheduler = AsyncIOScheduler()

    async def start(self):
        self.scheduler.start()

    async def stop(self):
        pass

    async def send_notification(self, message):
        pass

    def should_handle(self, message):
        pass

    async def handle_message(self, msg):
        pass

    async def plugin_schedule_task(self):
        pass