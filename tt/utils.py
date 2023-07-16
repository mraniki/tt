"""
 talky Utils
"""
__version__ = "3.11.4"

import asyncio
import importlib
import pkgutil
import schedule
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
            print(msg)
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
                module = importlib.import_module(
                    f"{package_name}.{plugin_name}")
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
    # PREPARING TO IMPLEMENT COMMANDS MAPPING ACROSS PLUGINS
    # ON HOLD FOR NOW
    # async def handle_message(self, msg):
    #     """
    #     Handles incoming messages.

    #     Args:
    #         msg (str): The incoming message.
    #     """
    #     if not self.enabled:
    #         return

    #     if msg.startswith(settings.bot_ignore):
    #         return

    #     if self.supports_fmo_search():
    #         if await self.fmo.search(msg):
    #             order = await self.fmo.get_order(msg)
    #             if order:
    #                 trade = await self.exchange.execute_order(order)
    #                 if trade:
    #                     await send_notification(trade)

    #     if msg.startswith(settings.bot_prefix):
    #         command, *args = msg.split(" ")
    #         command = command[1:]

    #         command_mapping = self.get_command_mapping()

    #         if command in command_mapping:
    #             function = command_mapping[command]
    #             await self.send_notification(f"{await function()}")

    # def get_command_mapping(self):
    #         """
    #         Returns the command mapping for the plugin.

    #         Override this method in subclasses to define the command mapping
    #         specific to that plugin.

    #         Returns:
    #             dict: The command mapping.
    #         """
    #         return {
    #             settings.bot_command_help: self.exchange.get_info,
    #             settings.bot_command_quote: lambda: self.exchange.get_quote(args[0]),
    #             settings.bot_command_bal: self.exchange.get_account_balance,
    #             settings.bot_command_pos: self.exchange.get_account_position,
    #             settings.bot_command_pnl_daily: self.exchange.get_account_pnl,
    #         }



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
