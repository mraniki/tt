import os
from tt.utils import BasePlugin, send_notification
from tt.config import logger, settings
import socket
import ping3

class NetworkPlugin(BasePlugin):
    name = os.path.splitext(os.path.basename(__file__))[0]
    def __init__(self):
        try:
            self.enabled = settings.network_enabled
            if self.enabled:
                logger.info("network_plugin initialized")
        except Exception as error:
            logger.warning(error)

    async def start(self):
        """Starts the plugin"""
        try:           
            if self.enabled:
                pass
        except Exception as error:
            logger.warning(error)
    
    async def stop(self):
        """Stops the plugin"""
        try:           
            if self.enabled:
                pass
        except Exception as error:
            logger.warning(error)

    async def send_notification(self, message):
        """Sends a notification"""
        try:           
            if self.enabled:
                await send_notification(message)
        except Exception as error:
            logger.warning(error)

    def should_handle(self, message):
        """Returns True if the plugin should handle incoming message"""
        return self.enabled

    async def handle_message(self, msg):
        """Handles incoming messages"""
        try:           
            if self.enabled:
                pass
        except Exception as error:
            logger.warning(error)
        # if self.enabled:
        # if msg == f"{settings.bot_prefix}{settings.bot_command_help}":
        #     await self.send_notification("this is an example from the example_plugin")
        # elif msg == f"{settings.bot_prefix}{settings.plugin_menu}":
        #     plugin_menu_message = f"⚙️:\n{settings.bot_prefix}{settings.plugin_menu}"
        #     await self.send_notification(plugin_menu_message)

    # def get_host_ip() -> str:
    #     """Returns host IP """
    #     try:
    #         s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #         s.connect((settings.ping, 80))
    #         ip_address = s.getsockname()[0]
    #         s.close()
    #         return ip_address
    #     except Exception:
    #         pass

    # def get_ping(host: str = settings.ping) -> float:
    #     """Returns latency """
    #     response_time = ping3.ping(host, unit='ms')
    #     time.sleep(1)
    #     return round(response_time, 3)