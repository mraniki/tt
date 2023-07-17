
import os
from tt.config import logger, settings
from tt.utils import send_notification
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

    async def start(self):
        """Starts the plugin"""
        logger.debug("plugin started")
        if self.enabled:
            logger.debug("plugin enabled")

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
