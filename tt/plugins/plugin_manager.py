
import importlib
import pkgutil

from asyncz.triggers import CronTrigger, IntervalTrigger

from tt.config import logger, scheduler, settings


class PluginManager:
    """🔌 Plugin Manager """
    def __init__(self, plugin_directory=None):
        self.plugin_directory = plugin_directory or settings.plugin_directory
        self.plugins = []

    def load_plugins(self):
        """ Load plugins from directory """
        package = importlib.import_module(self.plugin_directory)
        logger.debug("Loading plugins from: {}", package)
        for _, plugin_name, _ in pkgutil.iter_modules(package.__path__):
            try:
                module = importlib.import_module(
                    f"{self.plugin_directory}.{plugin_name}")
                logger.debug("Module loaded: {}", module)
                self.load_plugin(module, plugin_name)
            except Exception as e:
                logger.warning("Error loading plugin {}: {}", plugin_name, e)

    def load_plugin(self, module, plugin_name):
        """ Load a plugin from a module """
        logger.debug("plugin_name: {}", plugin_name)
        for name, obj in module.__dict__.items():
            if (isinstance(obj, type)
                    and issubclass(obj, BasePlugin)
                    and obj is not BasePlugin):
                plugin_instance = obj()
                self.plugins.append(plugin_instance)
                logger.info("Plugin loaded: {}", name)

    async def start_all_plugins(self):
        """ Start all plugins """
    
        for plugin in self.plugins:
            await self.start_plugin(plugin)
        scheduler.start()

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

                logger.error("process {}: {}", plugin, error)
                continue


class BasePlugin:
    """
    ⚡ Base Plugin Class
    """
    def __init__(self):
        self.enabled = False
        self.scheduler = scheduler

    async def start(self):
        pass

    async def stop(self):
        pass

    async def send_notification(self, message):
        pass

    def should_handle(self, message):
        return (not message.startswith(settings.bot_ignore)
         if self.enabled else False)

    async def plugin_notify_schedule_task(
        self,
        user_name=None,
        frequency=8,
        function=None):
        """Handles task notification 
        every X hours. Defaulted to 8 hours"""
        if function:
            self.scheduler.add_task(
                name=user_name,
                fn=self.send_notification,
                args=[f"{await function()}"],
                trigger=IntervalTrigger(hours=frequency),
                is_enabled=True
                )

    async def plugin_notify_cron_task(
        self,
        user_name=None,
        user_day_of_week="mon-fri",
        user_hours="8,12,16",
        user_timezone="UTC",
        function=None): 
        """Handles task cron scheduling for notification 
        monday to Friday at 8AM, 12PM and 4PM UTC based"""
        if function:
            self.scheduler.add_task(
                name=user_name,
                fn=self.send_notification,
                args=[f"{await function()}"],
                trigger=CronTrigger(
                    day_of_week=user_day_of_week,
                    hour=user_hours,
                    timezone=user_timezone),
                is_enabled=True
                )

    async def handle_message(self, msg):
        pass
        # if not self.should_handle(msg):
        #     return

        # command, *args = msg.split(" ")
        # command = command[1:]

        # command_mapping = self.get_command_mapping()

        # if command in command_mapping:
        #     function = command_mapping[command]
        #     await self.send_notification(f"{await function()}")