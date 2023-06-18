#import your lib
from tt.utils import BasePlugin, send_notification
from tt.config import logger, settings


class ExamplePlugin(BasePlugin):
    name = "example_plugin"
    def __init__(self):
        try:
            if settings.example_plugin_enabled:
                logger.info("plugin initialized")
        except Exception as e:
            logger.warning("init %s",e)

    async def start(self):
        """Starts the plugin"""
        try:           
            if settings.example_plugin_enabled:
                logger.info("plugin started")
        except Exception as e:
            logger.warning("start %s",e)

    async def stop(self):
        """Stops the plugin"""
        pass

    async def send_notification(self, message):
        """Sends a notification"""
        try:
            await send_notification(message)
        except Exception as e:
            logger.warning("plugin send_notification %s",e)

    def should_handle(self, message):
        """Returns True if the plugin should handle incoming message"""
        return False

    async def handle_message(self, msg):
        """Handles incoming messages"""
        if settings.example_plugin_enabled:
            if msg == f"{settings.bot_prefix}{settings.bot_command_help}":
                await self.send_notification("this is an example")
            elif msg == f"{settings.bot_prefix}{settings.plugin_menu}":
                plugin_menu_message = f"⚙️:\n{settings.bot_prefix}{settings.plugin_menu}"
                await self.send_notification(plugin_menu_message)
