from talkytrend import TalkyTrend
from tt.utils import BasePlugin, send_notification
from tt.config import logger, settings


class TalkyTrendPlugin(BasePlugin):
    name = "talkytrend_plugin"
    def __init__(self):
        try:
            if settings.talkytrend_enabled:
                self.trend = TalkyTrend()
        except Exception as e:
            logger.warning("talkytrend init %s",e)

    async def start(self):
        """Starts the TalkyTrend plugin"""
        try:           
            if settings.talkytrend_enabled:
                while True:
                    async for message in self.trend.scanner():
                        await self.send_notification(message)
        except Exception as e:
            logger.warning("talkytrend start %s",e)

    async def stop(self):
        """Stops the TalkyTrend plugin"""
        pass

    async def send_notification(self, message):
        """Sends a notification"""
        try:
            await send_notification(message)
        except Exception as e:
            logger.warning("talkytrend send_notification %s",e)

    def should_handle(self, message):
        """Returns True if the plugin should handle the message"""
        return True

    async def handle_message(self, msg):
        """Handles incoming messages"""
        if msg == f"{settings.bot_prefix}{settings.bot_command_news}":
            if self.trend.live_tv:
                await self.send_notification(f"📺: {self.trend.live_tv}")
            else:
                await self.send_notification("Not available.")
        elif msg == f"{settings.bot_prefix}{settings.bot_command_help}":
            help_message = f"📺:\n{settings.bot_prefix}{settings.bot_command_news}"
            await self.send_notification(help_message)
        elif msg == f"{settings.bot_prefix}{settings.plugin_menu}":
            plugin_menu_message = f"⚙️:\n{settings.bot_prefix}{settings.plugin_menu}"
            await self.send_notification(plugin_menu_message)
