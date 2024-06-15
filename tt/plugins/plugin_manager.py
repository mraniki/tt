import asyncio
import importlib
import pkgutil
from datetime import datetime

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

        # logger.debug("Processing: {}", message)
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
    This class is inherited by
    Talky Plugins
    for the scheduling,
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
        self.bot_prefix = settings.bot_prefix
        self.bot_ignore = settings.bot_ignore

    async def start(self):
        pass

    async def stop(self):
        pass

    async def send_notification(self, message):
        pass

    def should_handle(self, message):
        """
        Returns True if the plugin should handle the message
        if plugins is not enabled, ignore all messages
        else, ignore messages that do not have from bot_prefix
        or bot_ignore
        Args:
            message (str): Message

        Returns:
            bool

        """
        # if self.enabled:
        #     return (
        #         self.bot_ignore not in message or self.bot_prefix not in message
        #     )
        if self.enabled:
            logger.debug(f"Enabled: {self.enabled}")
            if self.bot_ignore:
                logger.debug(f"Bot Ignore: {self.bot_ignore}")
            if self.bot_prefix:
                logger.debug(f"Bot Prefix: {self.bot_prefix}")
            if self.bot_ignore not in message or self.bot_prefix not in message:
                logger.debug("Returning True")
                return True
            else:
                logger.debug("Returning False")
                return False
        else:
            logger.debug("Returning False (Plugin not enabled)")
            return False

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
        user_day_of_week=None,
        user_hours=None,
        user_timezone=None,
        function=None,
    ):
        """
        Handles task cron scheduling
        for notification
        default set to
        Tuesday to Thursday
        at 6AM, 12PM and 6PM UTC
        via settings

        Args:
            user_name (str): User name
            user_day_of_week (str): Day of week
            user_hours (str): Hours
            user_timezone (str): Timezone
            function (function): Function

        Returns:
            None

        """
        if not user_day_of_week:
            user_day_of_week = settings.user_day_of_week
        if not user_hours:
            user_hours = settings.user_hours
        if not user_timezone:
            user_timezone = settings.user_timezone

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
        Returns True if the current day and time
        are within the configured trading window.
        Use to control trading hours for plugins

        It allows to block order processing
        outside of trading hours defined in settings

        Returns:
            bool
        """
        if settings.trading_control:
            logger.debug("Trading control enabled")
            current_time = datetime.now().time()
            current_day = datetime.now().strftime("%a").lower()

            start_time = datetime.strptime(settings.trading_hours_start, "%H:%M").time()
            end_time = datetime.strptime(settings.trading_hours_end, "%H:%M").time()
            logger.debug(
                "Current time: {}, Current day: {}, Start time: {}, End time: {}",
                current_time,
                current_day,
                start_time,
                end_time,
            )
            return (
                current_day in settings.trading_days_allowed
                and start_time <= current_time <= end_time
            )

        return True
