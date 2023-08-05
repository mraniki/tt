"""
    www_plugin using Playwright

"""
import os

from playwright.async_api import async_playwright

from tt.config import logger, settings
from tt.plugins.plugin_manager import BasePlugin
from tt.utils import send_notification


class WwwPlugin(BasePlugin):
    """ www_plugin Plugin """
    name = os.path.splitext(os.path.basename(__file__))[0]
    def __init__(self):
        super().__init__()
        self.enabled = settings.www_enabled
        if self.enabled:
            self.version = "🎭"
            self.help_message = settings.www_commands

    async def start(self):
        """Starts the plugin"""

    async def stop(self):
        """Stops the plugin"""

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
                settings.bot_command_help: self.get_www_help,
                settings.bot_command_info: self.get_www_info,
                settings.bot_command_screenshot: self.get_www_run,
            }
            if command in command_mapping:
                function = command_mapping[command]
                await self.send_notification(f"{await function()}")

    async def get_www_help(self):
        """Help Message"""
        return f"{self.help_message}"

    async def get_www_info(self):
        """info Message"""
        return self.version

    async def get_www_run(self):
        """ 
        Gets the screenshot 
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(settings.www_url)
            logger.debug(await page.title())
            scr = await page.screenshot()
            await browser.close()
            return scr
