from talkytrend import TalkyTrend

from tt.config import settings
from tt.plugins.plugin_manager import BasePlugin
from tt.utils import send_notification


class TalkyTrendPlugin(BasePlugin):

    def __init__(self):
        super().__init__()
        self.enabled = settings.talkytrend_enabled
        if self.enabled:
            self.trend = TalkyTrend()

    async def start(self):
        """Starts the TalkyTrend plugin"""
        if self.enabled:
            await self.plugin_notify_cron_task(
                user_name="talky_monitor", function=self.trend.monitor
            )

    async def send_notification(self, message):
        """Sends a notification"""
        if self.enabled:
            await send_notification(message)

    async def handle_message(self, msg):
        """Handles incoming messages"""

        if self.should_not_handle(msg):
            return
        if msg.startswith(settings.bot_prefix):
            command, *args = msg.split(" ")
            command = command[1:]

            command_mapping = {
                settings.bot_command_info: self.trend.get_talkytrend_info,
                settings.bot_command_trend: self.trend.fetch_signal,
                settings.bot_command_news: self.trend.fetch_feed,
                settings.bot_command_tv: self.trend.get_tv,
                settings.bot_command_scraper: self.trend.scrape_page,
            }

            if command in command_mapping:
                function = command_mapping[command]
                await self.send_notification(f"{await function()}")
