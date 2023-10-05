import os
import socket
import sys

import ping3

from tt.config import settings
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
        super().__init__()
        self.enabled = settings.helper_enabled
        if self.enabled:
            self.host_ip = f"🕸 {self.get_host_ip()}"
            self.help_message = settings.helper_commands

    async def start(self):
        """Starts the plugin"""
        await self.send_notification(await self.get_helper_info())

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

    async def get_helper_info(self):
        """
        return info
        """
        return f"ℹ️ {type(self).__name__} {__version__}\n"

    async def get_helper_network(self):
        """
        :file:`/network` command to retrieve the network
        ping latency and
        the bot IP address
        """
        ping_result = ping3.ping(settings.ping, unit="ms")
        ping_result = round(ping_result, 2) if ping_result is not None else 0
        return f"️{self.host_ip}\n" f"🏓 {ping_result}\n"

    async def trading_switch_command(self):
        """
        Trading switch command
        :file:`/trading` command
        to turn off or on the
        trading capability
        """
        settings.trading_enabled = not settings.trading_enabled
        return f"Trading is {'enabled' if settings.trading_enabled else 'disabled'}."

    async def restart(self):
        """
        :file:`/restart` command
        to restart the bot
        """
        os.execl(sys.executable, os.path.abspath(__file__), sys.argv[0])

    def get_host_ip(self):
        """
        Returns bot IP
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((settings.ping, 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
