import asyncio
import os
import socket
import sys

import ping3

from tt.config import logger, settings
from tt.plugins.plugin_manager import BasePlugin
from tt.utils import __version__, send_notification


class HelperPlugin(BasePlugin):
    """
    Helper Plugin
    Provide multiple function
    such as giving the list of
    available command, network ping
    or restarting the bot

    network ping is using Ping3 lib
    more info: https://github.com/kyan001/ping3

    """

    name = os.path.splitext(os.path.basename(__file__))[0]

    def __init__(self):
        """
        Initialize the object.

        This function is the constructor of the class.
         It initializes the object by calling the parent
         class's constructor using the `super()` method.
          It also sets the `enabled` attribute
          to the value of the `helper_enabled` setting.

        If the `enabled` attribute is `True`,
        it sets the `host_ip` attribute to a
        formatted string that includes the result
        of the `get_host_ip()` method. It also sets
        the `help_message` attribute to the value
        of the `helper_commands` setting.
        """
        super().__init__()
        self.enabled = settings.helper_enabled
        if self.enabled:
            logger.info("Helper Plugin Enabled")
            self.host_ip = f"🕸 {self.get_host_ip()}"
            self.help_message = settings.helper_commands

    async def start(self):
        """Starts the plugin"""
        await self.send_notification(await self.get_helper_info())

    async def send_notification(self, message):
        """Sends a notification"""
        if self.enabled:
            await send_notification(message)

    async def handle_message(self, msg):
        """
        Handles a message received by the bot.

        Args:
            msg (str): The message received by the bot.

        Returns:
            None: If the message should not be handled.
            None: If the message is a command and
            the corresponding function is executed successfully.
            None: If the message is not a command.

        Supported functions are:

        - `get_helper_help()`
        - `get_helper_info()`
        - `get_helper_network()`
        - `trading_switch_command()`
        - `restart()`

        """
        if not self.should_handle(msg):
            return
        if msg.startswith(settings.bot_prefix):
            command, *args = msg.split(" ")
            command = command[1:]

            command_mapping = {
                settings.bot_command_help: self.get_helper_help,
                settings.bot_command_info: self.get_helper_info,
                settings.bot_command_network: self.get_helper_network,
                settings.bot_command_trading: self.trading_switch_command,
                settings.bot_command_restart: self.restart,
            }
            if command in command_mapping:
                function = command_mapping[command]
                await self.send_notification(f"{await function()}")

    async def get_helper_help(self):
        """
        Help Message
        :file:`/help` command to
        return the list of
        available command
        """
        return f"{self.help_message}"

    async def get_helper_info(self) -> str:
        """
        :file:`/info` command to
        return the name and version of the bot
        """
        return f"ℹ️ {settings.bot_name} {__version__}"

    async def get_helper_network(self) -> str:
        """
        :file:`/network` command to retrieve the network
        ping latency and
        the bot's public IP address
        """
        ping_result = ping3.ping(settings.ip_check_url, unit="ms")
        ping_result = round(ping_result, 2) if ping_result is not None else 0

        return f"🌐 {self.host_ip}\n" f"🏓 {ping_result} ms\n"

    async def trading_switch_command(self) -> str:
        """
        Trading switch command
        :file:`/trading` command
        to turn off or on the
        trading capability
        """
        settings.trading_enabled = not settings.trading_enabled
        status = "enabled" if settings.trading_enabled else "disabled"
        return f"ℹ️Trading is {status}."

    async def restart(self):
        """
        :file:`/restart` command
        to restart the bot
        """
        logger.info("Restarting...")
        asyncio.get_event_loop().stop()
        await asyncio.sleep(0.5)
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)

    @staticmethod
    def get_host_ip() -> str:
        """Returns bot IP address"""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 53))
            return s.getsockname()[0]
