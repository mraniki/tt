import asyncio
import importlib
import pkgutil

from asyncz.triggers import CronTrigger, IntervalTrigger

from tt.config import logger, scheduler, settings


class PluginManager:
    """
    🔌 Plugins are
    the core of Talky Trader,
    they are loaded at startup,
    to interact with the
    trading platform.

    Plugin Manager is used
    to load, start and
    dispatch message
    to the plugins

    Args:
        plugin_directory (str): Directory
        of plugins

    Returns:
        None

    """

    def __init__(self, plugin_directory=None):
        self.plugin_directory = plugin_directory or settings.plugin_directory
        self.plugins = []

    def load_plugins(self, plugin_names=None):
        """
        🔌Load plugins from directory

        Args:
            plugin_names (list): List of plugin names to load
            if None, load all plugins from self.plugin_directory
            You can use this to minimize the load time, memory and CPU.

        Returns:
            None

        Raises:
            Exception: If there was an error loading a plugin

        """
        package = importlib.import_module(self.plugin_directory)
        logger.debug("Loading plugins from: {}", package)
        if not plugin_names:
            plugin_names = [
                name for _, name, _ in pkgutil.iter_modules(package.__path__)
            ]

        for plugin_name in plugin_names:
            try:
                module = importlib.import_module(
                    f"{self.plugin_directory}.{plugin_name}"
                )
                self.load_plugin(module, plugin_name)
            except Exception as e:
                logger.warning("Error loading plugin {}: {}", plugin_name, e)

    def load_plugin(self, module, plugin_name):
        """
        Load a plugin from a module

        Args:
            module (Module): Module
            plugin_name (str): Plugin name

        Returns:
            None

        """
        for name, obj in module.__dict__.items():
            if (
                isinstance(obj, type)
                and issubclass(obj, BasePlugin)
                and obj is not BasePlugin
            ):
                plugin_instance = obj()
                self.plugins.append(plugin_instance)
                logger.debug("Plugin loaded: {}", name)

    async def start_all_plugins(self):
        """
        Start all plugins
        Start the scheduler

        Returns:
            None


        """

        for plugin in self.plugins:
            await self.start_plugin(plugin)
        scheduler.start()

    async def start_plugin(self, plugin):
        """
        Start a plugin

        Args:
            plugin (Plugin): Plugin

        Returns:
            None

        """
        await plugin.start()

    async def process_message(self, message):
        """
        Send message to plugins

        Args:
            message (str): Message

        Returns:
            None

        """

        logger.debug("Processing: {}", message)
        if not message:
            return
        tasks = []
        for plugin in self.plugins:
            try:
                if plugin.should_handle(message):
                    task = asyncio.create_task(plugin.handle_message(message))
                    tasks.append(task)
            except Exception as error:
                logger.error("process {}: {}", plugin, error)
        await asyncio.gather(*tasks)


class BasePlugin:
    """
    ⚡ Base Plugin Class
    use to be inherited by
    Talky Plugins
    especially the scheduling,
    notification and
    message handling.

    Scheduling is manage via asyncz lib
    More info: https://github.com/tarsil/asyncz

    Args:
        None

    Returns:
        None

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
        """
        Returns True if the plugin should handle the message

        Args:
            message (str): Message

        Returns:
            bool

        """
        if self.enabled:
            return not message.startswith(settings.bot_ignore)

    async def plugin_notify_schedule_task(
        self, user_name=None, frequency=8, function=None
    ):
        """
        Handles task notification
        every X hours. Defaulted to 8 hours

        Args:
            user_name (str): User name
            frequency (int): Frequency
            function (function): Function

        Returns:
            None
        """

        if function:
            self.scheduler.add_task(
                name=user_name,
                fn=self.send_notification,
                args=[f"{await function()}"],
                trigger=IntervalTrigger(hours=frequency),
                is_enabled=True,
            )

    async def plugin_notify_cron_task(
        self,
        user_name=None,
        user_day_of_week="tue-thu",
        user_hours="6,12,18",
        user_timezone="UTC",
        function=None,
    ):
        """
        Handles task cron scheduling
        for notification
        default set to
        Tuesday to Thursday
        at 6AM, 12PM and 6PM UTC

        Args:
            user_name (str): User name
            user_day_of_week (str): Day of week
            user_hours (str): Hours
            user_timezone (str): Timezone
            function (function): Function

        Returns:
            None

        """
        if function:
            self.scheduler.add_task(
                name=user_name,
                fn=self.send_notification,
                args=[f"{await function()}"],
                trigger=CronTrigger(
                    day_of_week=user_day_of_week,
                    hour=user_hours,
                    timezone=user_timezone,
                ),
                is_enabled=True,
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

    def should_handle_timeframe(self):
        """
        Returns True if it is 
        Tuesday, Wednesday, Thursday, 
        and time is between 8 to 16.

        Returns:
            bool
        """
        current_time = datetime.now().time()
        current_day = datetime.now().strftime("%a").lower()

        return current_day in ["tue", "wed", "thu"] and datetime.strptime("08:00", "%H:%M").time() <= current_time <= datetime.strptime("16:00", "%H:%M").time()