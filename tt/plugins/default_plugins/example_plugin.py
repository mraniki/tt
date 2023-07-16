import asyncio
import os
from tt.config import logger, settings
from tt.utils import send_notification, __version__
from tt.plugins.plugin_manager import BasePlugin

#from myclass import MyClass


class ExamplePlugin(BasePlugin):
    """Example Plugin
    Initialization of imported class MyClass
    """
    name = os.path.splitext(os.path.basename(__file__))[0]

    def __init__(self):
        """Plugin Initialization"""
        self.enabled = settings.example_plugin_enabled
        if self.enabled:
            logger.debug("plugin initialized")
            # self.myclass = MyClass()
        # self.schedule_enabled = settings.example_plugin_schedule_enabled
        # if self.schedule_enabled:
        #         self.schedule_manager = ScheduleManager(self)
        #         self.schedule_manager.schedule_example(
        #             self.myadhocfunction)
        #         self.schedule_manager.schedule_example_hourly(
        #             self.myadhocfunction)
        #         self.schedule_manager.schedule_example_every_8_hours(
        #             self.myadhocfunction)

    async def start(self):
        """Starts the plugin"""
        logger.debug("plugin started")
        if self.enabled:
            logger.debug("plugin enabled")
            # if self.schedule_enabled:
                # Start the schedule manager
                # asyncio.create_task(self.schedule_manager.run_schedule())

    async def stop(self):
        """Stops the plugin"""

    async def send_notification(self, message):
        """Sends a notification"""
        if self.enabled:
            await send_notification(message)

    def should_handle(self, message):
        """Returns plugin state"""
        return self.enabled

    async def handle_message(self, msg):
        """
        Handles incoming messages.

        Args:
            msg (str): The incoming message.
        """
        if self.enabled:
            if msg.startswith(settings.bot_ignore):
                return
            if msg.startswith(settings.bot_prefix):
                command, *args = msg.split(" ")
                command = command[1:]

                # Mapping of commands to functions
                command_mapping = {
                    settings.bot_command_help: self.myadhocfunction,
                    # settings.bot_command_myownfunction: self.myclass.myownfunction,
                }

                if command in command_mapping:
                    function = command_mapping[command]
                    await self.send_notification(f"{await function()}")

    async def myadhocfunction(self):
        """
        This is an example if you need an adhoc function.
        Your class object should be in the initialization.
        and the handle_message should be used to retrieve 
        your functions fro MyClass
        """
        return "this is an example"


    # NOT READY
    # def get_command_mapping(self):
    #     """
    #     Returns the command mapping for the plugin.

    #     Override this method to define the command mapping specific to this plugin.

    #     Returns:
    #         dict: The command mapping.
    #     """
    #     return {
    #         settings.bot_command_custom1: self.custom_function1,
    #         settings.bot_command_custom2: self.custom_function2,
    #     }