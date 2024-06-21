import asyncio
import importlib
import pkgutil
from datetime import datetime

from asyncz.triggers import CronTrigger, IntervalTrigger

from tt.config import logger, scheduler, settings
from tt.utils.notifications import Notifier


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
        self.notifier = Notifier()
        self.scheduler = scheduler
        self.bot_prefix = settings.bot_prefix
        self.bot_filter_out = settings.bot_ignore or []
        self.bot_filter_in = settings.bot_filter_in or []
        self.trading_control_message = settings.trading_control_message

    async def start(self):
        pass

    async def stop(self):
        pass

    async def send_notification(self, message):
        if self.enabled:
            await self.notifier.notify(message)

    def should_filter(self, message):
        """
        Returns True if the plugin should NOT handle the message
        if ignore characters are in the message via bot_ignore
        Args:
            message (str): Message

        Returns:
            bool

        """
        return any(message.startswith(word) for word in self.bot_filter_out)

    def should_filter_in(self, message):
        """
        Returns True if the given word is found in the message
        Args:
            message (str): Message
            word (str): Word to search for

        Returns:
            bool

        """
        return self.bot_filter_in in message

    def should_handle(self, message):
        """
        Determines if the plugin should handle
        the message based on certain conditions.

        Args:
            message (str): The message
            to be checked.

        Returns:
            bool: True if the plugin should
            handle the message, False otherwise.
        """
        if self.enabled:
            return True

    def is_command_to_handle(self, message):
        """
        Determines if the plugin should handle
        the message based on certain conditions.

        Args:
            message (str): The message to be checked.

        Returns:
            bool: True if the plugin should
            handle the message, False otherwise.
        """
        if message.startswith(settings.bot_prefix):
            return True

    async def plugin_notify_schedule_task(
        self, user_name=None, frequency=8, frequency_unit="hours", function=None
    ):
        """
        Handles task notification
        every X hours.
        Defaulted to 8 hours


        Args:
            user_name (str): User name
            frequency (int): Frequency
            frequency_unit (str): Frequency unit
            function (function): Function

        Returns:
            None
        """
        if frequency_unit == "hours":
            trigger = IntervalTrigger(hours=frequency)
        elif frequency_unit == "minutes":
            trigger = IntervalTrigger(minutes=frequency)
        else:
            raise ValueError("Invalid frequency unit. Must be 'hours' or 'minutes'.")

        if function:
            self.scheduler.add_task(
                name=user_name,
                fn=self.send_notification,
                args=[f"{await function()}"],
                trigger=trigger,
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
        """
        Handles an incoming message.

        Args:
            msg (str): The incoming message.

        Returns:
            None
        This is the function to use in your plugin to handle incoming messages.

        """
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
            control = (
                current_day in settings.trading_days_allowed
                and start_time <= current_time <= end_time
            )
            logger.debug("Trading control: {}", control)
            return control

        return True
