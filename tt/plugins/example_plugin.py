import asyncio
import os
from tt.utils import BasePlugin, send_notification
from tt.config import logger, settings
import schedule
#add your lib

class ExamplePlugin(BasePlugin):
    """Example Plugin"""
    name = os.path.splitext(os.path.basename(__file__))[0]
    def __init__(self):
        """Plugin Initialization"""
        self.enabled = settings.example_plugin_enabled
        self.schedule_enabled = settings.example_plugin_schedule_enabled
        if self.enabled:
            logger.debug("plugin initialized")

    async def start(self):
        """Starts the plugin"""       
        if self.enabled:
            logger.debug("plugin started")
            if self.schedule_enabled:
                self.schedule_notifications()

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
        """Handles incoming messages"""
        if self.enabled:
            if msg.startswith(settings.bot_ignore):
                return
            if msg.startswith(settings.bot_prefix):
                command = (msg.split(" ")[0])[1:]
                if command == settings.bot_command_help:
                    await self.send_notification("this is an example")

    def schedule_notifications(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.run_schedule())

    async def run_schedule(self):
        schedule.every().hour.do(
                lambda: asyncio.run(self.send_notification(
                    "this is a schedule example")))
        while True:
            schedule.run_pending()
            await asyncio.sleep(1)