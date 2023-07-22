import os

from talkytrend import TalkyTrend

from tt.config import settings
from tt.plugins.plugin_manager import BasePlugin
from tt.utils import send_notification


class TalkyTrendPlugin(BasePlugin):
    name = os.path.splitext(os.path.basename(__file__))[0]
    def __init__(self):
            super().__init__()  # Call the base class's __init__ method

            self.enabled = settings.talkytrend_enabled
            if self.enabled:
                self.trend = TalkyTrend()
                self.has_scheduled_jobs = True
            

    async def start(self):
        """Starts the TalkyTrend plugin"""  
        if self.enabled:
            await self.run_schedule()
            while True:
                async for message in self.trend.scanner():
                    await self.send_notification(message)

    async def stop(self):
        """Stops the TalkyTrend plugin"""

    async def send_notification(self, message):
        """Sends a notification"""
        if self.enabled:
            await send_notification(message)

    def should_handle(self, message):
        """Returns plugin status"""
        return self.enabled

    async def handle_message(self, msg):
        """Handles incoming messages"""
        if not self.enabled:
            return
        if msg.startswith(settings.bot_ignore):
            return
        if msg.startswith(settings.bot_prefix):
            command, *args = msg.split(" ")
            command = command[1:]

            command_mapping = {
                settings.bot_command_help: self.trend.get_talkytrend_help,
                settings.bot_command_info: self.trend.get_talkytrend_info,
                settings.bot_command_tv: self.trend.get_tv,
                settings.bot_command_trend: self.trend.check_signal,
                settings.bot_command_news: self.trend.fetch_key_feed,
            }

            if command in command_mapping:
                function = command_mapping[command]
                await self.send_notification(f"{await function()}")

    @BasePlugin.notify_hourly
    async def scheduled_function(self):
        """Hourly fetch the latest news"""
        await self.trend.fetch_key_feed()  