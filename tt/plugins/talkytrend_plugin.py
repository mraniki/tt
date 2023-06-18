import os
from tt.utils import BasePlugin, send_notification
from tt.config import logger, settings
from talkytrend import TalkyTrend

class TalkyTrendPlugin(BasePlugin):
    name = os.path.splitext(os.path.basename(__file__))[0]
    def __init__(self):
        try:
            self.enabled = settings.talkytrend_enabled
            if self.enabled:
                self.trend = TalkyTrend()
        except Exception as error:
            logger.warning(error)

    async def start(self):
        """Starts the TalkyTrend plugin"""
        try:           
            if self.enabled:
                while True:
                    async for message in self.trend.scanner():
                        await self.send_notification(message)
        except Exception as error:
            logger.warning(error)

    async def stop(self):
        """Stops the TalkyTrend plugin"""
        try:           
            if self.enabled:
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
        """Returns plugin status"""
        return self.enabled

    async def handle_message(self, msg):
        """Handles incoming messages"""
        try:
            if self.enabled:
                #move the below as part of the library
                if msg == f"{settings.bot_prefix}{settings.bot_command_news}":
                    if self.trend.live_tv:
                        await self.send_notification(f"📺: {self.trend.live_tv}")
                elif msg == f"{settings.bot_prefix}{settings.bot_command_help}":
                    help_message = f"📺:\n{settings.bot_prefix}{settings.bot_command_news}"
                    await self.send_notification(help_message)
                elif msg == f"{settings.bot_prefix}{settings.plugin_menu}":
                    plugin_menu_message = f"⚙️:\n{settings.bot_prefix}{settings.plugin_menu}"
                    await self.send_notification(plugin_menu_message)
        except Exception as error:
            logger.warning(error)
