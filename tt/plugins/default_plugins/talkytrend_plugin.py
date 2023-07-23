import os

from asyncz.schedulers.asyncio import AsyncIOScheduler
from asyncz.triggers import IntervalTrigger
from talkytrend import TalkyTrend

from tt.config import settings
from tt.plugins.plugin_manager import BasePlugin
from tt.utils import send_notification


class TalkyTrendPlugin(BasePlugin):
    name = os.path.splitext(os.path.basename(__file__))[0]
    def __init__(self):
        super().__init__()
        self.enabled = settings.talkytrend_enabled
        if self.enabled:
            self.scheduler = AsyncIOScheduler()
            self.trend = TalkyTrend()
            
    async def start(self):
        """Starts the TalkyTrend plugin"""  
        if self.enabled:
            await self.plugin_schedule_task()
            self.scheduler.start()

    async def stop(self):
        """Stops the TalkyTrend plugin"""

    async def send_notification(self, message):
        """Sends a notification"""
        if self.enabled:
            await send_notification(message)

    async def handle_message(self, msg):
        """Handles incoming messages"""

        if not self.should_handle(msg):
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

    async def plugin_schedule_task(self):
        """Handles task scheduling"""
        
        feed_data = await self.trend.fetch_key_feed()
        self.scheduler.add_task(
            fn=self.send_notification,
            args=[feed_data],
            trigger=IntervalTrigger(hours=8),
            max_instances=1,
            replace_existing=True,
            coalesce=True,
            is_enabled=True
            )
