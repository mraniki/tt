import os
import sys
import socket
import ping3
from tt.utils import BasePlugin, send_notification, __version__
from tt.config import logger, settings


class HelperPlugin(BasePlugin):
    name = os.path.splitext(os.path.basename(__file__))[0]
    def __init__(self):
        self.enabled = settings.helper_enabled
        if self.enabled:
            self.version = f"🗿 {__version__}\n"
            self.host_ip = self.get_host_ip()
            self.help_message = settings.bot_msg_help

    async def start(self):
        """Starts the plugin"""
        await self.send_notification(self.help_command())

    async def stop(self):
        """Stops the plugin"""
        pass

    async def send_notification(self, message):
        """Sends a notification"""
        if self.enabled:
            await send_notification(message)

    def should_handle(self, message):
        """Returns plugin status"""
        return self.enabled

    async def handle_message(self, msg):
        """Handles incoming messages"""
        if self.enabled:
            if msg.startswith(settings.bot_ignore):
                return
            if msg.startswith(settings.bot_prefix):
                command = (msg.split(" ")[0])[1:]
                if command == settings.bot_command_help:
                    await self.send_notification(self.help_command())
                elif command == settings.bot_command_trading:
                    await self.send_notification(self.trading_switch_command())
                elif command == settings.bot_command_restart:
                    os.execl(sys.executable, os.path.abspath(__file__), sys.argv[0])
    
    def help_command(self):
        """Help Message"""
        return (f"🗿 {self.version}\n"
                f"🕸️ {self.host_ip}\n"
                f"🏓 {round(ping3.ping(settings.ping, unit='ms'), 3)}\n"
                f"{self.help_message}")

    def trading_switch_command(self):
        """Trading switch command"""
        settings.trading_enabled = not settings.trading_enabled
        return f"Trading is {'enabled' if settings.trading_enabled else 'disabled'}."


    def get_host_ip(self):
        """Returns host IP """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((settings.ping, 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address