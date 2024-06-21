import asyncio
import os
import socket
import sys

import ping3

from tt.config import logger, settings
from tt.plugins.plugin_manager import BasePlugin
from tt.utils.version import __version__


class HelperPlugin(BasePlugin):
    """
    Helper Plugin
    Provide multiple function
    such as giving the list of
    available command, network ping
    or restarting the bot

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
            self.ip_check_url = settings.ip_check_url
            self.help_message = settings.helper_commands
            self.settings.trading_enabled = settings.settings.trading_enabled
            self.trading_status_message = settings.trading_status_message
            self.trading_status_enabled = settings.trading_status_enabled
            self.trading_status_disabled = settings.trading_status_disabled

    async def start(self):
        """
        Asynchronously starts the plugin
        by sending a notification using
        the `send_notification` method.
        The notification is obtained by
        calling the `get_helper_info` method asynchronously.

        Returns:
            None
        """
        await self.send_notification(await self.get_helper_info())

    async def handle_message(self, msg):
        """
        Handles incoming messages and
        routes them to the appropriate function.

        Args:
            msg (str): The message received by the plugin.

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
        if self.should_filter(msg):
            return
        elif self.is_command_to_handle(msg):
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
        :file:`/info` command to return
        the name and version of the bot
        and the list of enabled plugins
        and options

        #todo move all the settings in the init
        """
        return (
            f"ℹ️ {settings.bot_name} {__version__}\n"
            "______________________________\n"
            f"plugin_enabled: {settings.plugin_enabled}\n"
            f"plugins: {settings.plugin_directory}\n"
            f"ui_enabled: {settings.ui_enabled}\n"
            f"forwarder_enabled: {settings.forwarder}\n"
            f"trading_enabled: {self.trading_enabled}\n"
            f"trading_control: {settings.trading_control}\n"
            f"trading_days_allowed: {settings.trading_days_allowed}\n"
            f"trading_hours_start: {settings.trading_hours_start}\n"
            f"trading_hours_end: {settings.trading_hours_end}\n"
            f"trade action identifier: {settings.action_identifier}\n"
            f"trade default quantity: {settings.quantity}\n"
        )

    async def get_helper_network(self) -> str:
        """
        :file:`/network` command to retrieve the network
        ping latency and
        the bot's public IP address
        The network ping is using Ping3 lib
        more info: https://github.com/kyan001/ping3

        """
        ping_result = ping3.ping(self.ip_check_url, unit="ms")
        ping_result = round(ping_result, 2) if ping_result is not None else 0

        return f"🌐 {self.host_ip}\n" f"🏓 {ping_result} ms\n"

    async def trading_switch_command(self) -> str:
        """
        Trading switch command
        :file:`/trading` command
        to turn off or on the
        trading capability
        """
        self.trading_enabled = not self.trading_enabled
        status = "enabled" if self.trading_enabled else "disabled"
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
