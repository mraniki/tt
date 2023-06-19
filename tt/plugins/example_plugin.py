import os
from tt.utils import BasePlugin, send_notification
from tt.config import logger, settings
#add your lib

class ExamplePlugin(BasePlugin):
    """Example Plugin"""
    name = os.path.splitext(os.path.basename(__file__))[0]
    def __init__(self):
        """Plugin Initialization"""
        try:
            self.enabled = settings.example_plugin_enabled
            if self.enabled:
                logger.debug("plugin initialized")
        except Exception as error:
            logger.warning(error)

    async def start(self):
        """Starts the plugin"""
        try:           
            if self.enabled:
                logger.debug("plugin started")
        except Exception as error:
            logger.warning(error)

    async def stop(self):
        """Stops the plugin"""
        try:       
            pass
        except Exception as error:
            logger.warning(error)

    async def send_notification(self, message):
        """Sends a notification"""
        try:
            if self.enabled:
                await send_notification(message)
        except Exception as error:
            logger.warning(error)

    def should_handle(self, message):
        """Returns plugin state"""
        return self.enabled

    async def handle_message(self, msg):
        """Handles incoming messages"""
        if msg == f"{settings.bot_prefix}{settings.bot_command_help}":
            if self.enabled:
                await self.send_notification(
                    "this is an example")
