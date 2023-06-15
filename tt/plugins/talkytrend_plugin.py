from talkytrend import TalkyTrend
from tt.utils import BasePlugin, send_notification
from tt.config import logger, settings


class TalkyTrendPlugin(BasePlugin):
    def __init__(self):
        try:
            self.trend = TalkyTrend()
            logger.debug("plugin init TalkyTrend")
        except Exception as e:
            logger.warning("talkytrend init %s",e)

    def listening_for(self, msg):
        # This plugin listens for messages that start with the bot command prefix
        return msg.text.startswith(settings.bot_command_prefix)

    async def on_message_received(self, msg):
        """Handles incoming messages"""
        if msg.text == f"{settings.bot_command_prefix}{settings.bot_command_news}":
            if self.trend.live_tv:
                await self.send_notification(f"Live TV: {self.trend.live_tv}")
            else:
                await self.send_notification("Live TV is not available.")
        elif msg.text == f"{settings.bot_command_prefix}{settings.bot_command_help}":
            # Send a help message
            help_message = f"Available commands:\n{settings.bot_command_prefix}{settings.bot_command_news} - Shows the live TV URL."
            await self.send_notification(help_message)

    async def start(self):
        """Starts the TalkyTrend plugin"""
        logger.debug("talkytrend start TalkyTrend")
        try:
            while True:
                async for message in self.trend.scanner():
                    await self.send_notification(message)
        except Exception as e:
            logger.warning("talkytrend start %s",e)

    async def stop(self):
        """Stops the TalkyTrend plugin"""
        # Perform any necessary cleanup or shutdown tasks
        pass

    async def send_notification(self, message):
        """Sends a notification"""
        try:
            await send_notification(message)
        except Exception as e:
            logger.warning("talkytrend send_notification %s",e)