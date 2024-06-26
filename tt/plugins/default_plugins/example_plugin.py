from tt.config import logger, settings
from tt.plugins.plugin_manager import BasePlugin

# import MyClass / Your Class Object


class ExamplePlugin(BasePlugin):
    """Example Plugin
    Initialization of imported class MyClass
    """

    def __init__(self):
        """Plugin Initialization"""
        super().__init__()
        self.enabled = settings.example_plugin_enabled
        if self.enabled:
            logger.debug("example plugin enabled")
            # init MyClass here

    async def start(self):
        """Starts the plugin"""
        logger.debug("example plugin started")
        if self.enabled:
            logger.debug("example plugin enabled")

    async def handle_message(self, msg):
        """
        Handles incoming messages.

        Args:
            msg (str): The incoming message.
        """
        if self.should_filter(msg):
            return
        elif self.is_command_to_handle(msg):
            command, *args = msg.split(" ")
            command = command[1:]

            command_mapping = {
                self.bot_command_help: self.myadhocfunction,
                # self.bot_command_mycommand: self.Myclass.function,
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
